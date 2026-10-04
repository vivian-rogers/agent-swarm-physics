"""H16 library: trap states, reaction coordinate, Kramers/landscape estimators, kick dose laws, swarm bistability.

One set of definitions and estimators, used identically by the synthetic validation (`synthetic.py`), the per-period
exploratory pipeline (`run_period.py`) and the confirmatory script (`confirm.py`). Shared tables only
(data/processed/shared/); every loader takes an explicit list of PT dates and refuses holdout dates unless the caller
passes allow_holdout=True (only confirm.py with its two flags does).

Definitions (see the card, hypotheses/H16-metastable-traps-kramers/README.md, "Definitions"):
  active row   any agent event in events_core except WAIT and PAUSE, or any computer-use turn in `actions` except the
               `pause` tool call (it mirrors the PAUSE event; H09). Same rule as H09's idle_runs.
  TS1          inactive spell: a gap >= 180 s between consecutive active rows of one agent within one day's window.
               Starts at the last active row, ends at the next (escape) or at the window end (right-censored).
               The gap before the agent's first active row of the day is the cold start and is excluded.
  TS2          pause chain (regime III): maximal run of PAUSE events with no active row in between. Gate k = the k-th
               PAUSE's expiry decision: re-pause (next PAUSE comes before any active row) or escape (active row).
  TS3          error loop: run of consecutive error turns (`actions.error`), per agent-day; per-turn escape = next turn
               without error. Trap = run reaching 3 turns.
  TS4          identical-command loop: run of consecutive bash turns with an identical command hash (command text is
               hashed in memory, never stored), max 10 min between turns. Trap = run reaching 3 turns.
  RC           x_i(m) = EWMA (tau = 5 min) of the active-minute indicator a_i(m) (>= 1 active row in minute m).
  kicks        chat messages reaching the agent (`exposure`), classed with chat_mentions_clean.mentions_roster:
               A_und / A_men (agent speaker, not / mentioning the agent), H_und / H_men (human), N_tgt (automated naming
               the agent = nudge to it), N_by (automated naming others); automated with no valid mention = daily
               pause/resume bookend, dropped.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2" if _v == "POLARS_MAX_THREADS" else "1")

import datetime as dt
import json
import subprocess
from pathlib import Path

import numpy as np
import polars as pl
from scipy import optimize, special, stats

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H16-metastable-traps-kramers"
HDIR = ROOT / "hypotheses/H16-metastable-traps-kramers"
HOLDOUT = json.loads((ROOT / "hypotheses/holdout.json").read_text())
SEED = 20261003

MIN_GAP_S = 180.0          # TS1 threshold
BIN_S = 30.0               # hazard bin for TS1
LOOK_FAST_S = 120.0        # kick look-back (fast channel)
LOOK_SLOW_S = 900.0        # kick look-back (slow channel; H04 nudge plateau ~15 min)
LOOP_MIN = 3               # TS3/TS4 trap threshold (turns)
TS4_MAX_GAP_S = 600.0
TAU_RC = 5.0               # EWMA time constant (min)
NB_RC = 20                 # RC bins on [0, 1]
BURN_MIN = 15              # minutes dropped at the start of each day for the RC
KCLASSES = ("A_und", "A_men", "H_und", "H_men", "N_tgt", "N_by")
GLANCE_S = 120.0           # TS2r: re-pause within this long after waking counts as staying in the trap
DIRECTED = ("A_men", "H_men", "N_tgt")


# =============================================================================== days, periods, holdout

def calendar() -> pl.DataFrame:
    return pl.read_parquet(SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.Utf8))


def is_holdout_date(d: str, goal_no) -> bool:
    if goal_no is not None and int(goal_no) in set(HOLDOUT["goal_periods_held_out"]):
        return True
    return any(w["start"] <= d < w["end"] for w in HOLDOUT["ne_windows"])


def period_days(goal_no: int, allow_holdout: bool = False, date_from=None, date_to=None) -> list[str]:
    """Active PT dates of a goal period (window_s > 0). Holdout days are dropped unless allow_holdout."""
    c = calendar().filter((pl.col("goal_no") == goal_no) & (pl.col("window_s") > 0))
    if date_from:
        c = c.filter(pl.col("pt_date") >= date_from)
    if date_to:
        c = c.filter(pl.col("pt_date") < date_to)
    days = []
    for d, g, h in c.select("pt_date", "goal_no", "holdout").iter_rows():
        ho = bool(h) or is_holdout_date(d, g)
        if ho and not allow_holdout:
            continue
        days.append(d)
    return sorted(days)


def assert_no_holdout(days: list[str]):
    cal = calendar().filter(pl.col("pt_date").is_in(days))
    bad = [d for d, g, h in cal.select("pt_date", "goal_no", "holdout").iter_rows() if h or is_holdout_date(d, g)]
    if bad:
        raise RuntimeError(f"holdout leak: {bad[:5]} ... ({len(bad)} days)")


def _guard(days, allow_holdout):
    if not allow_holdout:
        assert_no_holdout(days)


def windows(days: list[str]) -> dict:
    cal = calendar().filter(pl.col("pt_date").is_in(days))
    out = {}
    for r in cal.iter_rows(named=True):
        out[r["pt_date"]] = dict(t0=r["win_start"].timestamp(), t1=r["win_end"].timestamp(), regime=r["regime"],
                                 goal_no=int(r["goal_no"] or 0), hours=r["documented_hours"], weekday=r["weekday"])
    return out


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--", "hypotheses/H16-metastable-traps-kramers"],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted-H16" if dirty.strip() else "")


def write_provenance(folder: Path, built_by: str, tables: list[str], params: dict):
    rev = None
    try:
        sp = json.loads((SH / "_provenance.json").read_text())
        for v in sp.values():
            if isinstance(v, dict) and isinstance(v.get("inputs"), dict) and v["inputs"].get("revision"):
                rev = v["inputs"]["revision"]
                break
    except Exception:
        pass
    prov = {"built_by": built_by, "git_commit": git_commit(),
            "inputs": [{"source": "ai-village (via data/processed/shared)", "revision": rev, "tables": tables}],
            "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "_provenance.json").write_text(json.dumps(prov, indent=1, default=str))


# =============================================================================== real-data loaders

def _roster_ok():
    ros = pl.read_parquet(SH / "roster.parquet")
    return set(ros.filter(~pl.col("claude_code"))["agent"].to_list())


def load_rows(days: list[str], allow_holdout=False) -> dict:
    """Per (agent, pt_date): sorted active-row times, PAUSE events (t, declared s), turns (t, error, cmd hash, is_bash).

    Times are float epoch seconds (UTC)."""
    _guard(days, allow_holdout)
    ok = _roster_ok()
    ev = (pl.read_parquet(SH / "events_core.parquet", columns=["t", "pt_date", "actor_kind", "agent", "action_type", "pause_s"])
          .filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null() & pl.col("pt_date").is_in(days))
          .with_columns(pl.col("action_type").cast(pl.Utf8).alias("k"), (pl.col("t").dt.epoch("us") / 1e6).alias("ts"))
          .filter(pl.col("agent").is_in(list(ok))))
    acts = (pl.read_parquet(SH / "actions.parquet", columns=["t", "agent", "action", "error"])
            .filter(pl.col("agent").is_not_null() & pl.col("agent").is_in(list(ok)))
            .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
            .filter(pl.col("pt_date").is_in(days) & (pl.col("action").cast(pl.Utf8) != "pause"))
            .with_columns((pl.col("t").dt.epoch("us") / 1e6).alias("ts"), (pl.col("action").cast(pl.Utf8) == "bash").alias("is_bash")))
    cmd = (pl.read_parquet(SH / "artifact_commands_text.parquet", columns=["t", "agent", "act", "cmd"])
           .filter((pl.col("act").cast(pl.Utf8) == "bash") & pl.col("cmd").is_not_null())
           .with_columns(pl.col("cmd").hash(seed=7).alias("h")).select("t", "agent", "h"))  # text dropped here
    acts = acts.join(cmd, on=["t", "agent"], how="left")
    W = windows(days)
    out = {}
    act_ev = ev.filter(~pl.col("k").is_in(["WAIT", "PAUSE"])).select("agent", "pt_date", "ts")
    pause_ev = ev.filter(pl.col("k") == "PAUSE").select("agent", "pt_date", "ts", "pause_s")
    wait_ev = ev.filter(pl.col("k") == "WAIT").select("agent", "pt_date", "ts")
    allact = pl.concat([act_ev, acts.select("agent", "pt_date", "ts")]).sort("agent", "pt_date", "ts")
    for (a, d), g in allact.group_by(["agent", "pt_date"]):
        if d not in W:
            continue
        w = W[d]
        t = g["ts"].to_numpy()
        t = t[(t >= w["t0"] - 1) & (t <= w["t1"] + 1)]
        out[(int(a), d)] = {"act": np.sort(t)}
    for (a, d), g in pause_ev.group_by(["agent", "pt_date"]):
        key = (int(a), d)
        if key in out:
            g = g.sort("ts")
            out[key]["pause_t"] = g["ts"].to_numpy()
            out[key]["pause_s"] = g["pause_s"].to_numpy().astype(float)
    for (a, d), g in wait_ev.group_by(["agent", "pt_date"]):
        key = (int(a), d)
        if key in out:
            out[key]["wait_t"] = np.sort(g["ts"].to_numpy())
    for (a, d), g in acts.sort("ts").group_by(["agent", "pt_date"]):
        key = (int(a), d)
        if key in out:
            out[key]["turn_t"] = g["ts"].to_numpy()
            out[key]["turn_err"] = g["error"].fill_null(False).to_numpy()
            out[key]["turn_bash"] = g["is_bash"].to_numpy()
            out[key]["turn_h"] = g["h"].fill_null(0).to_numpy().astype(np.uint64)
    for v in out.values():
        for k in ("pause_t", "wait_t", "turn_t"):
            v.setdefault(k, np.zeros(0))
        v.setdefault("pause_s", np.zeros(0))
        v.setdefault("turn_err", np.zeros(0, bool))
        v.setdefault("turn_bash", np.zeros(0, bool))
        v.setdefault("turn_h", np.zeros(0, np.uint64))
    return out


def load_kicks(days: list[str], allow_holdout=False) -> dict:
    """agent -> class -> sorted kick times (epoch s), on `days` (plus nothing else). Uses chat_mentions_clean."""
    _guard(days, allow_holdout)
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "speaker_kind"]).with_row_index("msg")
    men = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    assert chat.height == men.height and (chat["message_id"] == men["message_id"]).all(), "chat_mentions_clean misaligned"
    chat = chat.with_columns(men["mentions_roster"].alias("men")).filter(pl.col("pt_date").is_in(days))
    ex = pl.read_parquet(SH / "exposure.parquet", columns=["msg", "agent"]).join(chat, on="msg", how="inner")
    sk = pl.col("speaker_kind").cast(pl.Utf8)
    directed = pl.col("men").list.contains(pl.col("agent")).fill_null(False)
    has_valid = (pl.col("men").list.len().fill_null(0) > 0)
    ex = ex.with_columns(
        pl.when((sk == "agent") & directed).then(pl.lit("A_men"))
        .when(sk == "agent").then(pl.lit("A_und"))
        .when((sk == "human") & directed).then(pl.lit("H_men"))
        .when(sk == "human").then(pl.lit("H_und"))
        .when((sk == "automated") & directed).then(pl.lit("N_tgt"))
        .when((sk == "automated") & has_valid).then(pl.lit("N_by"))
        .otherwise(pl.lit("drop")).alias("kc"),
        (pl.col("t").dt.epoch("us") / 1e6).alias("ts"))
    out = {}
    for (a, c), g in ex.filter(pl.col("kc") != "drop").group_by(["agent", "kc"]):
        out.setdefault(int(a), {})[c] = np.sort(g["ts"].to_numpy())
    return out


def kick_counts(K: dict, agent: int, lo: np.ndarray, hi: np.ndarray, classes=KCLASSES) -> dict:
    """Counts of kicks of each class for `agent` in [lo, hi)."""
    out = {}
    ka = K.get(agent, {})
    for c in classes:
        arr = ka.get(c)
        if arr is None or len(arr) == 0:
            out[c] = np.zeros(len(lo), np.int16)
        else:
            out[c] = (np.searchsorted(arr, hi, "left") - np.searchsorted(arr, lo, "left")).astype(np.int16)
    return out


# =============================================================================== trap builders (work on synthetic too)

ISO_S = 120.0  # TS1r: an active row is isolated if no other active row lies within +-ISO_S


def robust_rows(t: np.ndarray, iso_s=ISO_S) -> np.ndarray:
    """Drop isolated active rows (core-set definition: escape needs >= 2 active rows within iso_s)."""
    if len(t) < 2:
        return t[:0]
    dl = np.r_[np.inf, np.diff(t)]
    dr = np.r_[np.diff(t), np.inf]
    return t[(dl <= iso_s) | (dr <= iso_s)]


def build_ts1(rows: dict, W: dict, K: dict | None = None, robust: bool = False) -> pl.DataFrame:
    """TS1 inactive spells (gap >= MIN_GAP_S between active rows); one row per spell.

    robust=True gives TS1r: isolated active rows (no other active row within +-120 s) do not end a spell."""
    recs = []
    for (a, d), v in rows.items():
        t = v["act"]
        if robust:
            t = robust_rows(t)
        if len(t) == 0 or d not in W:
            continue
        w = W[d]
        starts = t
        ends = np.r_[t[1:], w["t1"]]
        cens = np.r_[np.zeros(len(t) - 1, bool), True]
        gap = ends - starts
        m = gap >= MIN_GAP_S
        if not m.any():
            continue
        s0, s1, c = starts[m], ends[m], cens[m]
        pt = v.get("pause_t", np.zeros(0))
        wt = v.get("wait_t", np.zeros(0))
        npz = np.searchsorted(pt, s1, "left") - np.searchsorted(pt, s0, "right")
        nwt = np.searchsorted(wt, s1, "left") - np.searchsorted(wt, s0, "right")
        rec = {"agent": np.full(len(s0), a, np.int16), "pt_date": [d] * len(s0), "t0": s0, "t1": s1,
               "dwell_s": (s1 - s0).astype(np.float32), "censored": c, "n_pause": npz.astype(np.int16),
               "n_wait": nwt.astype(np.int16), "tod": ((s0 - w["t0"]) / max(w["t1"] - w["t0"], 1)).astype(np.float32),
               "first_act_s": np.full(len(s0), t[0] - w["t0"], np.float32)}
        if K is not None:
            kc = kick_counts(K, a, s0, s1)
            for cl, arr in kc.items():
                rec[f"n_{cl}"] = arr
        recs.append(pl.DataFrame(rec))
    if not recs:
        return pl.DataFrame()
    return pl.concat(recs, how="diagonal").sort("pt_date", "agent", "t0")


def ts1_hazard_rows(ts1: pl.DataFrame, K: dict | None, bin_s=BIN_S, t_min=MIN_GAP_S, look_fast=LOOK_FAST_S,
                    look_slow=LOOK_SLOW_S, max_elapsed_s=4 * 3600.0) -> dict:
    """Discrete-time at-risk rows for TS1 spells from elapsed t_min on, in bins of bin_s seconds.

    Returns dict of numpy arrays: y (escape in bin), elapsed (bin start, s), group ids (agent, agent-day), kick doses
    (fast window per class, slow window per class), spell index."""
    a = ts1["agent"].to_numpy(); d = ts1["pt_date"].to_list()
    t0 = ts1["t0"].to_numpy(); t1 = ts1["t1"].to_numpy(); cens = ts1["censored"].to_numpy()
    dur = t1 - t0
    nb = np.maximum(np.ceil((np.minimum(dur, max_elapsed_s) - t_min) / bin_s).astype(int), 0)
    idx = np.repeat(np.arange(len(t0)), nb)
    off = np.arange(nb.sum()) - np.repeat(np.cumsum(nb) - nb, nb)
    el = t_min + off * bin_s
    tb = t0[idx] + el
    last = off == (nb[idx] - 1)
    y = last & ~cens[idx] & (dur[idx] <= max_elapsed_s)
    out = {"y": y.astype(np.int8), "elapsed": el.astype(np.float32), "spell": idx, "agent": a[idx],
           "tod": ts1["tod"].to_numpy()[idx], "t": tb}
    dd = np.array(d)
    ad_keys = np.char.add(np.char.add(a.astype(str), "|"), dd)
    _, ad = np.unique(ad_keys, return_inverse=True)
    out["agentday"] = ad[idx]
    if K is not None:
        for cl in KCLASSES:
            out[f"f_{cl}"] = np.zeros(len(idx), np.int16)
            out[f"s_{cl}"] = np.zeros(len(idx), np.int16)
        for ag in np.unique(a):
            m = out["agent"] == ag
            kf = kick_counts(K, int(ag), tb[m] - look_fast, tb[m])
            ks = kick_counts(K, int(ag), tb[m] - look_slow, tb[m])
            for cl in KCLASSES:
                out[f"f_{cl}"][m] = kf[cl]
                out[f"s_{cl}"][m] = ks[cl]
    return out


def ts1_interval_rows(ts1: pl.DataFrame, K: dict, look=LOOK_FAST_S, grid_s=BIN_S, t_min=MIN_GAP_S,
                      max_elapsed_s=4 * 3600.0) -> dict:
    """Exact-time (counting-process) rows for TS1 spells (amendment A2, post hoc): each 30-s grid bin is further split
    at kick arrivals and at kick exits from the look-back window, so the dose is constant within an interval and kicks
    inside the escape bin that precede the escape are counted. Fit with cloglog and offset ln(interval length)."""
    out = {k: [] for k in ("y", "dt", "elapsed", "agent", "spell")}
    for c in ("directed", "undirected"):
        out[c] = []
    groups = {"directed": ("A_men", "H_men", "N_tgt"), "undirected": ("A_und", "H_und")}
    a_ = ts1["agent"].to_numpy(); t0_ = ts1["t0"].to_numpy(); t1_ = ts1["t1"].to_numpy(); c_ = ts1["censored"].to_numpy()
    cache = {}
    for i in range(len(a_)):
        a, t0, t1, cens = int(a_[i]), t0_[i], t1_[i], bool(c_[i])
        lo, hi = t0 + t_min, min(t1, t0 + max_elapsed_s)
        if hi <= lo:
            continue
        if a not in cache:
            ka = K.get(a, {})
            cache[a] = {g: np.sort(np.concatenate([ka.get(c, np.zeros(0)) for c in cl])) for g, cl in groups.items()}
        full = cache[a]
        arrs = {}
        for g_, arr_ in full.items():
            i0, i1 = np.searchsorted(arr_, lo - look - 1.0), np.searchsorted(arr_, hi + 1.0)
            arrs[g_] = arr_[i0:i1]
        bps = [np.arange(lo, hi, grid_s)]
        for g, arr in arrs.items():
            sel = arr[(arr > lo - look) & (arr < hi)]
            bps.append(sel[(sel > lo) & (sel < hi)])
            ex = sel + look
            bps.append(ex[(ex > lo) & (ex < hi)])
        b = np.unique(np.concatenate(bps + [np.array([lo, hi])]))
        st, en = b[:-1], b[1:]
        keep = en - st > 1e-6
        st, en = st[keep], en[keep]
        n = len(st)
        y = np.zeros(n, np.int8)
        if not cens and t1 <= t0 + max_elapsed_s:
            y[-1] = 1
        out["y"].append(y); out["dt"].append(en - st); out["elapsed"].append(st - t0)
        out["agent"].append(np.full(n, a)); out["spell"].append(np.full(n, i))
        for g, arr in arrs.items():
            # dose at interval start (counts kicks in (t - look, t]; kicks at exactly st count)
            out[g].append((np.searchsorted(arr, st, "right") - np.searchsorted(arr, st - look, "right")).astype(np.int16))
    return {k: (np.concatenate(v) if v else np.zeros(0)) for k, v in out.items()}


def build_ts2(rows: dict, W: dict, K: dict | None = None, early_tol_s=30.0) -> pl.DataFrame:
    """TS2 gates: one row per PAUSE event inside a pause chain."""
    recs = []
    for (a, d), v in rows.items():
        pt, ps, act = v.get("pause_t", np.zeros(0)), v.get("pause_s", np.zeros(0)), v["act"]
        if len(pt) == 0 or d not in W:
            continue
        w = W[d]
        nxt_act = np.searchsorted(act, pt, "right")
        t_next_act = np.where(nxt_act < len(act), act[np.minimum(nxt_act, len(act) - 1)], np.inf)
        t_next_p = np.r_[pt[1:], np.inf]
        # chain id: new chain when an active row lies between consecutive pauses
        prev_act_idx = np.r_[-1, nxt_act[:-1]]
        new_chain = np.r_[True, nxt_act[1:] != nxt_act[:-1]]
        chain = np.cumsum(new_chain) - 1
        k = np.zeros(len(pt), int)
        for i in range(len(pt)):
            k[i] = 1 if new_chain[i] else k[i - 1] + 1
        repause = t_next_p < t_next_act
        decl = np.where(np.isfinite(ps) & (ps > 0), ps, np.nan)
        expiry = pt + np.nan_to_num(decl, nan=1e7)
        t_gate = np.where(repause, t_next_p, np.minimum(t_next_act, w["t1"]))
        escape = ~repause & np.isfinite(t_next_act) & (t_next_act <= w["t1"] + 1)
        censored = ~repause & ~escape
        early = escape & (t_next_act < expiry - early_tol_s)
        # TS2r (amendment 2026-10-03): a "glance" (waking and pausing again within GLANCE_S) is a re-pause
        wake = np.where(np.isfinite(t_next_act), np.minimum(t_next_act, np.maximum(expiry, pt)), expiry)
        wake = np.where(t_next_p < wake, t_next_p, wake)
        rep_r = (t_next_p - np.maximum(wake, np.minimum(expiry - early_tol_s, wake))) <= GLANCE_S
        rep_r = rep_r | repause
        cens_r = ~rep_r & ((wake + GLANCE_S > w["t1"]) | ~np.isfinite(t_next_act) | (t_next_act > w["t1"]))
        esc_r = ~rep_r & ~cens_r
        new_r = np.r_[True, ~rep_r[:-1]]
        chain_r = np.cumsum(new_r) - 1
        k_r = np.zeros(len(pt), int)
        for i in range(len(pt)):
            k_r[i] = 1 if new_r[i] else k_r[i - 1] + 1
        rec = {"agent": np.full(len(pt), a, np.int16), "pt_date": [d] * len(pt), "chain": chain.astype(np.int32),
               "k": k.astype(np.int16), "chain_r": chain_r.astype(np.int32), "k_r": k_r.astype(np.int16),
               "outcome_r": np.where(rep_r, "repause", np.where(esc_r, "escape", "censored")),
               "t_pause": pt, "declared_s": decl.astype(np.float32), "t_gate": t_gate,
               "outcome": np.where(repause, "repause", np.where(early, "early", np.where(escape, "escape", "censored"))),
               "tod": ((pt - w["t0"]) / max(w["t1"] - w["t0"], 1)).astype(np.float32)}
        if K is not None:
            hi = np.minimum(t_gate, np.where(np.isfinite(decl), expiry, t_gate))
            kc = kick_counts(K, a, pt, hi)
            ks = kick_counts(K, a, hi - LOOK_SLOW_S, hi)
            for cl in KCLASSES:
                rec[f"n_{cl}"] = kc[cl]
                rec[f"s_{cl}"] = ks[cl]
        recs.append(pl.DataFrame(rec))
    if not recs:
        return pl.DataFrame()
    df = pl.concat(recs, how="diagonal").sort("pt_date", "agent", "t_pause")
    # next declared duration within the chain (trap deepening)
    df = df.with_columns(pl.col("declared_s").shift(-1).over("pt_date", "agent", "chain").alias("next_declared_s"),
                         pl.col("declared_s").shift(-1).over("pt_date", "agent", "chain_r").alias("next_declared_r_s"))
    return df


def build_turn_loops(rows: dict, W: dict, K: dict | None, kind: str) -> pl.DataFrame:
    """TS3 (kind='err') or TS4 (kind='cmd'): per-turn rows inside loops, from the loop's first turn on.

    Row = the k-th consecutive looping turn; y = 1 if the next turn breaks the loop; censored if the day ends."""
    recs = []
    for (a, d), v in rows.items():
        tt = v.get("turn_t", np.zeros(0))
        if len(tt) < 2 or d not in W:
            continue
        if kind == "err":
            t = tt
            flag = v["turn_err"].astype(bool)
            same_next = flag[1:]
            in_loop = flag
            cont = np.r_[same_next, False]          # next turn continues the loop
            brk_gap = np.zeros(len(t), bool)
        else:
            m = v["turn_bash"].astype(bool)
            t = tt[m]
            h = v["turn_h"][m]
            if len(t) < 2:
                continue
            valid = h != 0
            gap_next = np.r_[np.diff(t), np.inf]
            same = np.r_[(h[1:] == h[:-1]) & valid[1:] & valid[:-1], False]
            brk_gap = gap_next > TS4_MAX_GAP_S
            cont = same & ~brk_gap
            in_loop = valid
        # run index k: consecutive turns linked by cont
        k = np.zeros(len(t), int)
        for i in range(len(t)):
            if not in_loop[i]:
                k[i] = 0
            elif i > 0 and k[i - 1] > 0 and cont[i - 1]:
                k[i] = k[i - 1] + 1
            else:
                k[i] = 1
        if kind == "cmd":
            # a command loop exists only once a repeat happened: rows from k = 2 on (turn 2 is the first repeat)
            sel = k >= 2
        else:
            sel = k >= 1
        if not sel.any():
            continue
        idx = np.nonzero(sel)[0]
        last = idx == len(t) - 1
        y = (~cont[idx]) & ~last
        cens = last | (brk_gap[idx] & (kind == "err"))
        t_next = np.r_[t[1:], W[d]["t1"]][idx]
        run_start = np.zeros(len(t), int)
        for i in range(len(t)):
            run_start[i] = i if k[i] <= 1 else run_start[i - 1]
        rec = {"agent": np.full(len(idx), a, np.int16), "pt_date": [d] * len(idx), "k": k[idx].astype(np.int16),
               "t": t[idx], "dt_next_s": (t_next - t[idx]).astype(np.float32), "y": y.astype(np.int8),
               "censored": cens, "run": (run_start[idx]).astype(np.int32),
               "tod": ((t[idx] - W[d]["t0"]) / max(W[d]["t1"] - W[d]["t0"], 1)).astype(np.float32)}
        if K is not None:
            kc = kick_counts(K, a, t[idx], t_next - 2.0)
            for cl in KCLASSES:
                rec[f"n_{cl}"] = kc[cl]
        recs.append(pl.DataFrame(rec))
    if not recs:
        return pl.DataFrame()
    return pl.concat(recs, how="diagonal").sort("pt_date", "agent", "t")


def minute_activity(rows: dict, W: dict) -> dict:
    """pt_date -> (agents array, A matrix n_agents x n_min int8). Agents with >= 1 active row that day only."""
    by_day = {}
    for (a, d), v in rows.items():
        if d in W and len(v["act"]):
            by_day.setdefault(d, []).append((a, v["act"]))
    out = {}
    for d, lst in by_day.items():
        w = W[d]
        n_min = int(np.ceil((w["t1"] - w["t0"]) / 60.0))
        lst.sort()
        A = np.zeros((len(lst), n_min), np.int8)
        for i, (a, t) in enumerate(lst):
            mi = np.floor((t - w["t0"]) / 60.0).astype(int)
            mi = mi[(mi >= 0) & (mi < n_min)]
            A[i, mi] = 1
        out[d] = (np.array([a for a, _ in lst], np.int16), A)
    return out


# =============================================================================== GLM with fixed effects

def glm_fe(y, X, g=None, link="cloglog", max_iter=60, tol=1e-9, offset=None):
    """Binary GLM (cloglog: grouped proportional hazards; or logit) with group fixed effects profiled by Schur complement.

    Groups without variation in y are dropped (they carry no information on beta under FE). Returns dict with beta,
    se, cov, loglik, n, n_groups."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    n, p = X.shape
    if g is None:
        g = np.zeros(n, int)
    g = np.asarray(g)
    _, g = np.unique(g, return_inverse=True)
    G = g.max() + 1
    off = np.zeros(n) if offset is None else np.asarray(offset, float)
    sy = np.bincount(g, y, G); cn = np.bincount(g, None, G)
    keep_g = (sy > 0) & (sy < cn)
    m = keep_g[g]
    y, X, g, off = y[m], X[m], g[m], off[m]
    if len(y) == 0 or y.sum() == 0:
        return {"beta": np.full(p, np.nan), "se": np.full(p, np.nan), "cov": np.full((p, p), np.nan), "loglik": np.nan,
                "n": 0, "n_groups": 0, "n_events": 0}
    _, g = np.unique(g, return_inverse=True)
    G = g.max() + 1
    ybar = np.clip(np.bincount(g, y, G) / np.bincount(g, None, G), 1e-4, 1 - 1e-4)
    alpha = np.log(-np.log1p(-ybar)) if link == "cloglog" else np.log(ybar / (1 - ybar))
    beta = np.zeros(p)

    def mu_d(eta):
        if link == "cloglog":
            ee = np.exp(np.clip(eta, -30, 5))
            mu = -np.expm1(-ee)
            dmu = ee * np.exp(-ee)
        else:
            mu = special.expit(eta)
            dmu = mu * (1 - mu)
        mu = np.clip(mu, 1e-12, 1 - 1e-12)
        return mu, np.maximum(dmu, 1e-300)

    def ll(alpha, beta):
        mu, _ = mu_d(alpha[g] + X @ beta + off)
        return float(np.sum(y * np.log(mu) + (1 - y) * np.log1p(-mu)))

    if offset is not None:
        alpha = alpha - np.bincount(g, off, G) / np.bincount(g, None, G)
    cur = ll(alpha, beta)
    S = np.eye(p)
    failed = False
    stalled = False
    for it in range(max_iter):
        eta = alpha[g] + X @ beta + off
        mu, dmu = mu_d(eta)
        var = mu * (1 - mu)
        wr = (y - mu) * dmu / var
        W_ = dmu ** 2 / var
        sa = np.bincount(g, wr, G)
        sb = X.T @ wr
        Hd = np.bincount(g, W_, G) + 1e-12
        Hab = np.stack([np.bincount(g, W_ * X[:, j], G) for j in range(p)], axis=1)
        Hbb = X.T @ (W_[:, None] * X)
        S = Hbb - Hab.T @ (Hab / Hd[:, None])
        rhs = sb - Hab.T @ (sa / Hd)
        try:
            db = np.linalg.solve(S + 1e-10 * np.eye(p), rhs)
        except np.linalg.LinAlgError:
            db = np.linalg.lstsq(S, rhs, rcond=None)[0]
        da = (sa - Hab @ db) / Hd
        step = 1.0
        for _ in range(30):
            na, nb_ = alpha + step * da, beta + step * db
            new = ll(na, nb_)
            if np.isfinite(new) and new >= cur - 1e-10:
                break
            step /= 2
        alpha, beta = na, nb_
        stalled = (step < 1e-6) and np.any(np.abs(db) > 1e-3 * (1 + np.abs(beta)))
        conv = abs(new - cur) < tol * (1 + abs(cur))
        cur = new
        if conv and it > 1:
            break
    if stalled:
        failed = True
    try:
        cov = np.linalg.pinv(S)
    except np.linalg.LinAlgError:
        cov = np.full((p, p), np.nan)
    se0 = np.sqrt(np.maximum(np.diag(cov), 0))
    if failed and np.any((np.abs(beta) > 8) | (se0 > 4)):
        failed = False          # divergence comes from separated coefficients only; they are blanked below
    if failed or not np.all(np.isfinite(beta)):
        beta = np.full(p, np.nan)
        cov = np.full((p, p), np.nan)
    se = np.sqrt(np.maximum(np.diag(cov), 0))
    # complete separation: coefficient runs off; flag and blank it
    sep = (np.abs(beta) > 8) | (se > 4)
    beta = np.where(sep, np.nan, beta)
    return {"beta": beta, "se": np.where(sep, np.nan, se), "cov": cov, "loglik": cur, "n": int(len(y)),
            "n_groups": int(G), "n_events": int(y.sum()), "separated": sep.tolist(), "failed": failed}


def dose_dummies(n, top=3):
    n = np.minimum(np.asarray(n), top)
    return np.stack([(n == k).astype(float) for k in range(1, top + 1)], axis=1)


def deep_rate(ts1: pl.DataFrame, el_min=600.0):
    """Escape rate (per min) from TS1/TS1r spells in the trap regime: events after el_min / exposure beyond el_min."""
    d = ts1["dwell_s"].to_numpy(); c = ts1["censored"].to_numpy()
    expo = np.maximum(d - el_min, 0).sum() / 60.0
    ev = int(((d >= el_min) & ~c).sum())
    return (ev / expo if expo > 0 else float("nan")), ev, float(expo)


def dose_law(lhr, cov, doses):
    """Compare dose laws on dose-specific log hazard ratios (vs dose 0) by minimum distance.

    kramers: ln HR_n = b n (barrier lowered linearly per kick -> hazard exponential in dose)
    additive: HR_n = 1 + c n (independent triggers)
    saturating: HR_n = 1 + c (1 - exp(-n / n0))."""
    lhr = np.asarray(lhr, float); doses = np.asarray(doses, float)
    ok = np.isfinite(lhr)
    if ok.sum() < 2 or not np.all(np.isfinite(cov[np.ix_(ok, ok)])):
        return {"ok": False}
    l, C, n = lhr[ok], cov[np.ix_(ok, ok)], doses[ok]
    Ci = np.linalg.pinv(C)

    def chi(f):
        r = l - f
        return float(r @ Ci @ r)
    out = {"ok": True, "lhr": lhr.tolist(), "doses": doses.tolist(), "se": np.sqrt(np.diag(cov)).tolist()}
    # kramers (linear, closed form GLS)
    b = float((n @ Ci @ l) / (n @ Ci @ n))
    out["kramers"] = {"b": b, "chi2": chi(b * n), "k": 1}
    r = optimize.minimize_scalar(lambda c: chi(np.log(np.maximum(1 + c * n, 1e-9))), bounds=(-1 / n.max() + 1e-6, 50),
                                 method="bounded")
    out["additive"] = {"c": float(r.x), "chi2": float(r.fun), "k": 1}
    best = None
    for n0 in (0.3, 0.7, 1.5, 3.0):
        rr = optimize.minimize(lambda q: chi(np.log(np.maximum(1 + q[0] * (1 - np.exp(-n / np.exp(q[1]))), 1e-9))),
                               [max(np.exp(l.max()) - 1, 0.1), np.log(n0)], method="Nelder-Mead")
        if best is None or rr.fun < best.fun:
            best = rr
    out["saturating"] = {"c": float(best.x[0]), "n0": float(np.exp(best.x[1])), "chi2": float(best.fun), "k": 2}
    aic = {m: out[m]["chi2"] + 2 * out[m]["k"] for m in ("kramers", "additive", "saturating")}
    out["best_aic"] = min(aic, key=aic.get)
    out["aic"] = aic
    if ok[0] and ok[1] and abs(lhr[0]) > 1e-9:
        out["kappa"] = float(lhr[1] / lhr[0])   # kramers: 2; additive: ln(2HR1-1)/ln HR1 < 2
    return out


# =============================================================================== survival helpers

def km(d, cens):
    """Kaplan-Meier: returns times, survival."""
    d = np.asarray(d, float); e = ~np.asarray(cens, bool)
    o = np.argsort(d)
    d, e = d[o], e[o]
    ut = np.unique(d[e])
    S, s = [], 1.0
    for t in ut:
        at = np.sum(d >= t)
        ev = np.sum((d == t) & e)
        s *= 1 - ev / at
        S.append(s)
    return ut, np.array(S)


def km_median(d, cens):
    t, S = km(d, cens)
    i = np.nonzero(S <= 0.5)[0]
    return float(t[i[0]]) if len(i) else float("nan")


def km_rmst(d, cens, tau):
    t, S = km(d, cens)
    tt = np.r_[0, t[t < tau], tau]
    SS = np.r_[1, S[t < tau]]
    return float(np.sum(np.diff(tt) * SS))


def hazard_curve(y, el, edges):
    """Pooled discrete hazard per elapsed bin (rows already at risk)."""
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (el >= lo) & (el < hi)
        n = int(m.sum())
        out.append({"lo": float(lo), "hi": float(hi), "n": n, "h": float(y[m].mean()) if n else float("nan")})
    return out


# =============================================================================== reaction coordinate and landscape

def ewma(A: np.ndarray, tau=TAU_RC) -> np.ndarray:
    """Row-wise causal EWMA of a 0/1 matrix (agents x minutes); x(0) = a(0)."""
    al = 1 - np.exp(-1.0 / tau)
    X = np.zeros(A.shape, np.float64)
    X[:, 0] = A[:, 0]
    for m in range(1, A.shape[1]):
        X[:, m] = (1 - al) * X[:, m - 1] + al * A[:, m]
    return X


def rc_pairs(series: list[np.ndarray], burn=BURN_MIN):
    """Collect (x_t, x_{t+1}) pairs and occupancy values from per-agent-day x series after burn-in."""
    x0, x1, occ = [], [], []
    for x in series:
        x = x[burn:]
        if len(x) < 3:
            continue
        occ.append(x)
        x0.append(x[:-1]); x1.append(x[1:])
    if not occ:
        return np.zeros(0), np.zeros(0), np.zeros(0)
    return np.concatenate(x0), np.concatenate(x1), np.concatenate(occ)


def landscape(occ, nb=NB_RC, smooth=3, min_barrier=0.3, min_mass=0.02):
    """Boltzmann inversion G = -ln P on nb bins of [0,1]; locate trap well (low x), active well, barrier."""
    edges = np.linspace(0, 1 + 1e-9, nb + 1)
    c = np.histogram(occ, edges)[0].astype(float)
    mass = c / max(c.sum(), 1)
    if smooth > 1:
        k = np.ones(smooth) / smooth
        ms = np.convolve(np.r_[mass[0], mass, mass[-1]], k, mode="same")[1:-1]
    else:
        ms = mass
    ms = np.maximum(ms, 0.5 / max(c.sum(), 1))
    G = -np.log(ms / ms.sum())
    centers = 0.5 * (edges[1:] + edges[:-1])
    # local minima (boundaries allowed)
    Gp = np.r_[np.inf, G, np.inf]
    mins = [i for i in range(nb) if Gp[i + 1] <= Gp[i] and Gp[i + 1] <= Gp[i + 2]]
    res = {"centers": centers.tolist(), "G": G.tolist(), "mass": mass.tolist(), "n": int(c.sum()), "double_well": False}
    if len(mins) < 2:
        res["reason"] = "single minimum"
        return res
    a = mins[0]
    if centers[a] > 0.5:
        res["reason"] = "no low-x well"
        return res
    later = [i for i in mins[1:] if centers[i] - centers[a] >= 0.2]
    if not later:
        res["reason"] = "wells too close"
        return res
    b = min(later, key=lambda i: G[i])
    s = a + int(np.argmax(G[a:b + 1]))
    dG = G[s] - G[a]
    dG_b = G[s] - G[b]
    ma = mass[max(a - 1, 0):a + 2].sum(); mb = mass[max(b - 1, 0):b + 2].sum()
    res.update({"ia": int(a), "ib": int(b), "is": int(s), "xa": float(centers[a]), "xb": float(centers[b]),
                "xs": float(centers[s]), "dG": float(dG), "dG_back": float(dG_b), "mass_a": float(ma), "mass_b": float(mb)})
    res["double_well"] = bool(dG >= min_barrier and dG_b >= min_barrier and ma >= min_mass and mb >= min_mass)
    if not res["double_well"]:
        res["reason"] = "shallow"
    return res


def km_coeffs(x0, x1, nb=NB_RC, min_n=30):
    """Kramers-Moyal drift F and diffusion D per bin from 1-min increments (D = Var(dx | x) / 2)."""
    edges = np.linspace(0, 1 + 1e-9, nb + 1)
    b = np.clip(np.digitize(x0, edges) - 1, 0, nb - 1)
    dx = x1 - x0
    n = np.bincount(b, None, nb)
    F = np.bincount(b, dx, nb) / np.maximum(n, 1)
    M2 = np.bincount(b, dx * dx, nb) / np.maximum(n, 1)
    D = np.maximum(M2 - F ** 2, 1e-12) / 2
    F[n < min_n] = np.nan
    D[n < min_n] = np.nan
    return F, D, n


def mfpt_1d(mass, D, ia, ib, nb=NB_RC):
    """Mean first-passage time (min) from bin ia to bin ib (> ia) for a 1D diffusion with reflecting boundary at 0,
    using the empirical stationary density (occupancy) and diffusion D(x):
        T = int_{xa}^{xb} dy / (D(y) P(y)) int_0^y P(z) dz."""
    dx = 1.0 / nb
    P = np.asarray(mass, float) / dx
    Dv = np.asarray(D, float).copy()
    if np.any(~np.isfinite(Dv[ia:ib + 1])):
        good = np.isfinite(Dv)
        if good.sum() < 2:
            return float("nan")
        Dv = np.interp(np.arange(nb), np.nonzero(good)[0], Dv[good])
    cum = np.cumsum(mass) - 0.5 * np.asarray(mass)
    T = 0.0
    for j in range(ia, ib):
        jj = j + 0.5  # integrate over bin j -> j+1 using midpoint values
        Pj = 0.5 * (P[j] + P[j + 1]); Dj = 0.5 * (Dv[j] + Dv[j + 1]); Cj = 0.5 * (cum[j] + cum[j + 1])
        if Pj <= 0 or Dj <= 0:
            return float("nan")
        T += dx * Cj / (Dj * Pj)
    return float(T)


def kramers_saddle(G, D, ia, is_, ib, nb=NB_RC):
    """Kramers saddle-point time 2 pi exp(dG) / (D(x_s) sqrt(G''_a |G''_s|)); curvatures by local quadratic fits."""
    x = (np.arange(nb) + 0.5) / nb
    G = np.asarray(G)

    def curv(i):
        lo, hi = max(i - 2, 0), min(i + 3, nb)
        if hi - lo < 3:
            return np.nan
        c = np.polyfit(x[lo:hi], G[lo:hi], 2)
        return 2 * c[0]
    ca, cs = curv(ia), curv(is_)
    if not (np.isfinite(ca) and np.isfinite(cs)) or ca <= 0 or cs >= 0 or not np.isfinite(D[is_]):
        return float("nan")
    return float(2 * np.pi * np.exp(G[is_] - G[ia]) / (D[is_] * np.sqrt(ca * abs(cs))))


def msm_mfpt(x0, x1, ia, ib, nb=NB_RC):
    """MFPT (min) from bin ia to the set of bins >= ib for the empirical 1-min Markov chain on RC bins."""
    edges = np.linspace(0, 1 + 1e-9, nb + 1)
    b0 = np.clip(np.digitize(x0, edges) - 1, 0, nb - 1)
    b1 = np.clip(np.digitize(x1, edges) - 1, 0, nb - 1)
    C = np.zeros((nb, nb))
    np.add.at(C, (b0, b1), 1)
    rs = C.sum(1)
    T = np.divide(C, rs[:, None], out=np.zeros_like(C), where=rs[:, None] > 0)
    S = [i for i in range(ib) if rs[i] > 0]
    if ia not in S:
        return float("nan")
    Q = T[np.ix_(S, S)]
    try:
        t = np.linalg.solve(np.eye(len(S)) - Q, np.ones(len(S)))
    except np.linalg.LinAlgError:
        return float("nan")
    return float(t[S.index(ia)])


def msm2_mfpt(x0, x1, a0, a1, ia, ib, nb=NB_RC):
    """MFPT (min) for the 2D Markov embedding (RC bin, current-minute activity a): from (ia, a=0) to any bin >= ib.

    The EWMA alone is not Markov (rising and falling trajectories share x); adding a(t) restores the Markov property
    for a 2-state alternating process with constant hazards."""
    edges = np.linspace(0, 1 + 1e-9, nb + 1)
    b0 = np.clip(np.digitize(x0, edges) - 1, 0, nb - 1) * 2 + a0.astype(int)
    b1 = np.clip(np.digitize(x1, edges) - 1, 0, nb - 1) * 2 + a1.astype(int)
    ns = 2 * nb
    C = np.zeros((ns, ns))
    np.add.at(C, (b0, b1), 1)
    rs = C.sum(1)
    T = np.divide(C, rs[:, None], out=np.zeros_like(C), where=rs[:, None] > 0)
    S = [i for i in range(2 * ib) if rs[i] > 0]
    start = 2 * ia
    if start not in S:
        return float("nan")
    Q = T[np.ix_(S, S)]
    try:
        t = np.linalg.solve(np.eye(len(S)) - Q, np.ones(len(S)))
    except np.linalg.LinAlgError:
        return float("nan")
    return float(t[S.index(start)])


def first_passage_obs(series: list[np.ndarray], xa_hi: float, xb_lo: float, burn=BURN_MIN):
    """Observed passages: start when x enters x <= xa_hi, stop when x >= xb_lo; censored at day end.

    Returns (durations in min, censored flags)."""
    durs, cens = [], []
    for x in series:
        x = x[burn:]
        inside = False
        t0 = 0
        for m in range(len(x)):
            if not inside and x[m] <= xa_hi:
                inside, t0 = True, m
            elif inside and x[m] >= xb_lo:
                durs.append(m - t0); cens.append(False); inside = False
        if inside:
            durs.append(len(x) - 1 - t0); cens.append(True)
    return np.array(durs, float), np.array(cens, bool)


def exp_rate(durs, cens):
    """Exponential MLE of the passage rate (per min) and its implied MFPT; with Poisson CI on the count."""
    tot = float(np.sum(durs)); ne = int(np.sum(~cens))
    if tot <= 0 or ne == 0:
        return {"k": float("nan"), "mfpt": float("nan"), "n_events": ne, "time": tot}
    lo, hi = stats.chi2.ppf(0.025, 2 * ne) / 2, stats.chi2.ppf(0.975, 2 * ne + 2) / 2
    return {"k": ne / tot, "mfpt": tot / ne, "n_events": ne, "time": tot, "k_lo": lo / tot, "k_hi": hi / tot}


def rc_cell(series: list[np.ndarray], nb=NB_RC, acts: list[np.ndarray] | None = None):
    """Full landscape / Kramers analysis for one cell (list of per-agent-day x series; optional matching 0/1 series)."""
    x0, x1, occ = rc_pairs(series)
    if len(occ) < 500:
        return {"ok": False, "n": int(len(occ))}
    L = landscape(occ, nb)
    F, D, n = km_coeffs(x0, x1, nb)
    out = {"ok": True, "n": int(len(occ)), "landscape": L, "F": F.tolist(), "D": D.tolist()}
    if not L["double_well"]:
        return out
    ia, is_ = L["ia"], L["is"]
    ib = min(is_ + 1, L["ib"])           # product core starts just past the barrier top
    edges = np.linspace(0, 1, nb + 1)
    durs, cens = first_passage_obs(series, edges[ia + 1], edges[ib])
    obs = exp_rate(durs, cens)
    T1 = mfpt_1d(L["mass"], D, ia, ib, nb)
    TK = 0.5 * kramers_saddle(L["G"], D, ia, is_, ib, nb)  # MFPT to the barrier top = half the transition time
    TM = msm_mfpt(x0, x1, ia, ib, nb)
    TM2 = float("nan")
    if acts is not None:
        a0, a1, _ = rc_pairs([a.astype(float) for a in acts])
        TM2 = msm2_mfpt(x0, x1, a0, a1, ia, ib, nb)
    # drift-potential barrier in units of T_eff: int F/D dx from a to s (should equal dG for a 1D diffusion)
    Fi = np.asarray(F); Di = np.asarray(D)
    seg = slice(ia, is_ + 1)
    ratio = Fi[seg] / Di[seg]
    dU_over_T = float(-np.nansum(ratio) / nb) if np.isfinite(ratio).sum() >= 2 else float("nan")
    Teff = float(np.nanmean(Di[max(ia - 1, 0):ia + 2]))
    out.update({"target_bin": int(ib), "obs": obs, "mfpt_1d": T1, "mfpt_kramers": TK, "mfpt_msm": TM, "mfpt_msm2": TM2, "dU_over_T_drift": dU_over_T,
                "T_eff_well": Teff, "n_passages": int(len(durs)), "frac_censored": float(cens.mean()) if len(cens) else float("nan")})
    return out


# =============================================================================== swarm-level bimodality

def bimodality_stats(v, nbins):
    v = np.asarray(v, float)
    n = len(v)
    if n < 10 or np.std(v) == 0:
        return {"bc": float("nan"), "valley": 0.0, "n_modes": 1}
    g1 = stats.skew(v); g2 = stats.kurtosis(v)
    bc = (g1 ** 2 + 1) / (g2 + 3 * (n - 1) ** 2 / ((n - 2) * (n - 3)))
    h = np.histogram(v, np.linspace(0, 1 + 1e-9, nbins + 1))[0].astype(float)
    k = np.exp(-0.5 * (np.arange(-3, 4) / 1.2) ** 2); k /= k.sum()
    hs = np.convolve(np.r_[h[2::-1], h, h[:-4:-1]], k, mode="same")[3:-3]
    pk = [i for i in range(nbins) if hs[i] > 0 and (i == 0 or hs[i] > hs[i - 1]) and (i == nbins - 1 or hs[i] >= hs[i + 1])]
    valley = 0.0
    if len(pk) >= 2:
        top = sorted(pk, key=lambda i: hs[i], reverse=True)[:2]
        i, j = sorted(top)
        vmin = hs[i:j + 1].min()
        valley = float(1 - vmin / min(hs[i], hs[j]))
    return {"bc": float(bc), "valley": valley, "n_modes": int(len(pk))}


def swarm_analysis(MA: dict, rng, n_sur=200, burn=BURN_MIN, tail=10, lag=30, exclude_stalls=False, jitter=15, null="dayswap"):
    """null='dayswap' (pre-registered): agent-wise day swap with +-jitter min; null='circ' (amendment A4, post hoc):
    within-day circular shift of each agent's series (>= 30 min), which keeps each agent's activity level on that day
    (so day-level common fields survive in the null) but not the within-day schedule profile."""
    """Swarm activity m(t) per minute vs the agent-wise day-swap null (keeps each agent's schedule profile and
    autocorrelation, destroys within-day cross-agent timing)."""
    days = sorted(MA)
    if len(days) < 2:
        return {"ok": False}
    lens = np.array([MA[d][1].shape[1] for d in days])
    L = int(np.median(lens))
    days = [d for d, l in zip(days, lens) if l >= 0.8 * L]
    L = min(MA[d][1].shape[1] for d in days)
    agents = sorted(set(int(a) for d in days for a in MA[d][0]))
    ai = {a: i for i, a in enumerate(agents)}
    nA, nD = len(agents), len(days)
    S = np.full((nA, nD, L), -1, np.int8)   # -1 = absent
    for j, d in enumerate(days):
        ag, A = MA[d]
        for r, a in enumerate(ag):
            S[ai[int(a)], j, :] = A[r, :L]
    sl = slice(burn, L - tail)
    pres = S[:, :, 0] >= 0          # agent present on day
    Npres = pres.sum(0)

    def m_of(Sx):
        act = np.where(Sx[:, :, sl] > 0, 1, 0)
        K = act.sum(0)                  # days x minutes
        return K, K / np.maximum(Npres[:, None], 1)
    K, m = m_of(S)
    stall = (K == 0)
    # surrogates: for each agent present on day j, take its series from another day where present (same minutes)
    sur_m, sur_K = [], []
    tt = np.arange(L)
    for s in range(n_sur):
        Sx = np.full_like(S, -1)
        if null == "circ":
            core = np.arange(burn, L - tail)
            Sx[:] = S
            for i in range(nA):
                for j in np.nonzero(pres[i])[0]:
                    sh = int(rng.integers(30, max(len(core) - 30, 31)))
                    Sx[i, j, core] = np.roll(S[i, j, core], sh)
            Kx, mx = m_of(Sx)
            sur_K.append(Kx); sur_m.append(mx)
            continue
        for i in range(nA):
            dd = np.nonzero(pres[i])[0]
            if len(dd) < 2:
                Sx[i, dd] = S[i, dd]
                continue
            perm = dd.copy()
            for _ in range(10):
                perm = rng.permutation(dd)
                if np.all(perm != dd):
                    break
            for j, jp in zip(dd, perm):
                sh = int(rng.integers(-jitter, jitter + 1)) if jitter else 0
                Sx[i, j] = S[i, jp, np.clip(tt + sh, 0, L - 1)]
        Kx, mx = m_of(Sx)
        sur_K.append(Kx); sur_m.append(mx)
    sur_K = np.array(sur_K); sur_m = np.array(sur_m)
    EK = sur_K.mean(0); VK = sur_K.var(0)
    mask = ~stall if exclude_stalls else np.ones_like(stall, bool)
    r = (K - EK)
    VR = float(np.sum(r[mask] ** 2) / np.sum(VK[mask]))
    # single-spin variance <1 - m_i^2> = 4 <p_i (1 - p_i)> from the independent null
    phi = float(4 * np.sum(VK[mask]) / np.sum(np.broadcast_to(Npres[:, None], VK.shape)[mask]))
    bj = float((1 - 1 / VR) / max(phi, 1e-6))
    # null calibration of VR: treat surrogates as data (their own deviation from the surrogate mean)
    vr_null = [float(np.sum((sur_K[s_][mask] - EK[mask]) ** 2) / np.sum(VK[mask])) for s_ in range(min(n_sur, 100))]
    VRc = VR / max(float(np.median(vr_null)), 1e-9)
    bj_c = float((1 - 1 / VRc) / max(phi, 1e-6))
    nbins = int(np.clip(np.median(Npres) + 1, 8, 33))
    obs = bimodality_stats(m[mask], nbins)
    null = [bimodality_stats(sur_m[s][mask], nbins) for s in range(n_sur)]
    out = {"ok": True, "n_days": nD, "minutes_per_day": int(L - burn - tail), "n_agents_median": float(np.median(Npres)),
           "VR_cond": VR, "VR_null_p95": float(np.percentile(vr_null, 95)), "VR_null_median": float(np.median(vr_null)), "phi": phi,
           "betaJ0_raw": bj, "betaJ0": bj_c, "mean_m": float(m.mean()), "stall_frac": float(stall.mean()), "obs": obs}
    for key in ("bc", "valley", "n_modes"):
        nv = np.array([z[key] for z in null], float)
        out[f"null_{key}_p95"] = float(np.nanpercentile(nv, 95))
        out[f"null_{key}_mean"] = float(np.nanmean(nv))
        out[f"p_{key}"] = float((np.sum(nv >= obs[key]) + 1) / (len(nv) + 1))
    # branch memory: residual autocorrelation at `lag` min vs surrogates
    def acf_lag(R, lag):
        a, b = R[:, :-lag].ravel(), R[:, lag:].ravel()
        a = a - a.mean(); b = b - b.mean()
        return float((a * b).mean() / np.sqrt((a * a).mean() * (b * b).mean() + 1e-12))
    out["acf_obs"] = acf_lag(r.astype(float), lag)
    accs = [acf_lag((sur_K[s] - EK).astype(float), lag) for s in range(min(n_sur, 100))]
    out["acf_null_mean"] = float(np.mean(accs)); out["acf_null_p95"] = float(np.percentile(accs, 95))
    out["hist_obs"] = np.histogram(m[mask], np.linspace(0, 1 + 1e-9, nbins + 1))[0].tolist()
    out["hist_null"] = np.mean([np.histogram(sur_m[s][mask], np.linspace(0, 1 + 1e-9, nbins + 1))[0] for s in range(n_sur)], 0).tolist()
    return out


# =============================================================================== misc

def day_bootstrap(units: np.ndarray, rng, B: int):
    """Yield index arrays resampling unique units (days) with replacement."""
    u = np.unique(units)
    pos = {x: np.nonzero(units == x)[0] for x in u}
    for _ in range(B):
        pick = rng.choice(u, len(u), replace=True)
        yield np.concatenate([pos[x] for x in pick])


def jdump(obj, path: Path):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, (np.bool_,)):
            return bool(o)
        return str(o)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=conv))
