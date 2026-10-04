"""H112 scheme library: switch-ins, co-switch pairs, awareness classes and departures (codes only, no text).

Definitions (card, "Data scheme"):
  switch-in (action, call-level)  an action touch of project P by agent a at t when a's previous touch that PT day was
                                  another project and a did not touch P in the previous 60 min (H104's arrival rule at
                                  touch resolution). Work channel: H104's switch (work arrival) on DQ4 agent commits.
  co-switch                       two switch-ins onto the same P by different agents on the same PT day, lag <= 15 min;
                                  each switch-in is paired at most once (greedy by lag, earliest first).
  claims                          agent chat messages strictly naming P (project_mentions_chat): by i in
                                  [t_i - 15 min, t_j), by j in [t_j - 15 min, t_i)
  awareness class                 read      a claim of the partner was seen by the agent's switch call
                                            (its receiving call for that agent has t_call <= the switch call's t_call)
                                  inflight  a partner claim existed before the switch but neither switch call saw it
                                  silent    no partner claim existed before either switch
  departure within K calls        the agent's label at its K-th call after t* = t_j (most recent touch before the next
                                  call's t_call; no touch = stays) differs from P. Censored if the agent has < K + 1
                                  calls after t* on that PT day.

All builders take frames, so the synthetic worlds (analysis/synthetic.py) run through the same code.
Holdout days are dropped (common.holdout_mask) unless allow_holdout=True (confirm.py only).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import hashlib  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import OUT as SHARED, holdout_mask  # noqa: E402

CLAUDE_CODE = 19
STRICT = ["url", "output", "bare"]
US = 1_000_000
W_PAIR = 15 * 60          # co-switch window (s)
W_CLAIM = 15 * 60         # claim look-back (s)
REVISIT = 3600            # no touch of P in the previous 60 min
KS = (5, 10, 20)
LAG_BINS = (0, 60, 300, 901)
WORK_HORIZON = 3600


def phash(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()[:10]


# ============================================================================================ real-data inputs
def period_days(goal_no: int, allow_holdout: bool = False) -> list[str]:
    cal = pl.read_parquet(SHARED / "calendar.parquet", columns=["pt_date", "goal_no"]).filter(pl.col("goal_no") == goal_no)
    days = cal["pt_date"].to_list()
    if not allow_holdout:
        ho = holdout_mask(days, [goal_no] * len(days))
        days = [d for d, h in zip(days, ho) if not h]
    return sorted(days)


def _with_pt(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))


def load_touches(goal_no: int, days: list[str]) -> pl.DataFrame:
    """Strict action touches: agent, t, pt_date, project (parent repo/site)."""
    from project_states import project_map
    am = pl.scan_parquet(SHARED / "artifact_mentions.parquet").select("artifact", "t", "agent", "source", "how")
    am = am.filter((pl.col("source").cast(pl.String) == "action") & pl.col("how").cast(pl.String).is_in(STRICT)
                   & (pl.col("agent") >= 0) & (pl.col("agent") != CLAUDE_CODE)).collect()
    am = _with_pt(am.join(project_map(), on="artifact", how="inner")).filter(pl.col("pt_date").is_in(days))
    return am.select("agent", "t", "pt_date", "project").sort("agent", "t")


def load_claims(goal_no: int, days: list[str]) -> pl.DataFrame:
    pm = pl.read_parquet(SHARED / "project_mentions_chat.parquet", columns=["message_id", "t", "pt_date", "agent", "project"])
    pm = pm.filter(pl.col("pt_date").is_in(days) & (pl.col("agent") >= 0) & (pl.col("agent") != CLAUDE_CODE))
    return pm.unique(["message_id", "project"]).sort("t")


def load_work(goal_no: int, days: list[str]) -> pl.DataFrame:
    wc = pl.scan_parquet(SHARED / "work_commits.parquet").select("repo", "t", "pt_date", "author_agent", "author_kind",
                                                                 "automated", "canonical", "imported")
    wc = wc.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")
                   & pl.col("pt_date").is_in(days)).collect()
    return wc.select(pl.col("author_agent").alias("agent"), "t", "pt_date", pl.col("repo").cast(pl.String).alias("project")) \
        .filter(pl.col("agent") != CLAUDE_CODE).sort("agent", "t")


def load_calls_period(goal_no: int, days: list[str]) -> pl.DataFrame:
    cw = pl.scan_parquet(SHARED / "call_windows.parquet").select("turn_id", "agent", "t_call", "pt_date", "ctx_mode")
    cw = cw.filter(pl.col("pt_date").is_in(days) & (pl.col("ctx_mode").cast(pl.String) != "summary")
                   & (pl.col("agent") != CLAUDE_CODE)).collect()
    return cw.select("agent", "t_call", "pt_date", "turn_id").sort("agent", "t_call", "turn_id")


def load_receipts(message_ids: list[str], days: list[str]) -> pl.DataFrame:
    from visibility import receipts
    if not message_ids:
        return pl.DataFrame(schema={"message_id": pl.String, "recipient": pl.Int8, "t_recv": pl.Datetime("us", "UTC")})
    r = receipts(message_ids)
    r = r.filter(pl.col("rc_date").is_in(days))
    return r.select("message_id", "recipient", pl.col("t_call").alias("t_recv"))


def calls_dict(calls: pl.DataFrame) -> dict:
    """agent -> (t_call us sorted, pt_date array)."""
    out = {}
    for (a,), g in calls.group_by(["agent"], maintain_order=True):
        out[int(a)] = (g["t_call"].dt.epoch("us").to_numpy(), g["pt_date"].to_numpy())
    return out


# ============================================================================================ events
def switch_ins(touches: pl.DataFrame) -> pl.DataFrame:
    ev = touches.sort("agent", "t").with_columns(
        pl.col("project").shift(1).over("agent", "pt_date").alias("prev"),
        pl.col("t").shift(1).over("agent", "project").alias("t_prev_same"))
    sw = ev.filter(pl.col("prev").is_not_null() & (pl.col("prev") != pl.col("project"))
                   & (pl.col("t_prev_same").is_null() | ((pl.col("t") - pl.col("t_prev_same")).dt.total_seconds() > REVISIT)))
    return sw.select("agent", "t", "pt_date", "project").with_row_index("sid")


def pair_switches(sw: pl.DataFrame, w: float = W_PAIR) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Greedy nearest-partner pairing; returns (pairs, solo switch-ins)."""
    a = sw.select("sid", "agent", "t", "pt_date", "project")
    j = a.join(a, on=["pt_date", "project"], suffix="_b").filter(
        (pl.col("agent") != pl.col("agent_b")) & (pl.col("t_b") >= pl.col("t")) & (pl.col("sid") != pl.col("sid_b"))
        & ((pl.col("t_b") - pl.col("t")).dt.total_seconds() <= w))
    j = j.with_columns(((pl.col("t_b") - pl.col("t")).dt.total_seconds()).alias("lag")).sort("lag", "t", "sid", "sid_b")
    used: set[int] = set()
    keep = []
    for r in j.select("sid", "sid_b").iter_rows():
        if r[0] in used or r[1] in used:
            continue
        used.add(r[0]); used.add(r[1]); keep.append(r)
    if keep:
        kp = pl.DataFrame({"sid": [k[0] for k in keep], "sid_b": [k[1] for k in keep]},
                          schema={"sid": j.schema["sid"], "sid_b": j.schema["sid_b"]})
        pairs = j.join(kp, on=["sid", "sid_b"], how="inner").sort("t")
    else:
        pairs = j.head(0)
    # solo: no other agent's switch-in onto P within +-w
    near = a.join(a, on=["pt_date", "project"], suffix="_b").filter(
        (pl.col("agent") != pl.col("agent_b")) & ((pl.col("t_b") - pl.col("t")).dt.total_seconds().abs() <= w))
    solo = a.filter(~pl.col("sid").is_in(near["sid"].unique().implode()))
    pairs = pairs.rename({"agent": "ai", "t": "ti", "sid": "si", "agent_b": "aj", "t_b": "tj", "sid_b": "sj"})
    return pairs.with_row_index("pid"), solo


def producing_t(t_us: np.ndarray, agents: np.ndarray, cd: dict) -> np.ndarray:
    """t_call (us) of the latest call with t_call < t (strict); -1 if none."""
    out = np.full(len(t_us), -1, np.int64)
    for a in np.unique(agents):
        v = cd.get(int(a))
        if v is None:
            continue
        ca = v[0]
        m = np.flatnonzero(agents == a)
        k = np.searchsorted(ca, t_us[m], side="left") - 1
        ok = k >= 0
        out[m[ok]] = ca[k[ok]]
    return out


def classify(pairs: pl.DataFrame, claims: pl.DataFrame, rec: pl.DataFrame, cd: dict, w_claim: float = W_CLAIM) -> pl.DataFrame:
    if len(pairs) == 0:
        return pairs.with_columns(pl.lit(None, pl.String).alias("cls"))
    ti = pairs["ti"].dt.epoch("us").to_numpy(); tj = pairs["tj"].dt.epoch("us").to_numpy()
    pairs = pairs.with_columns(pl.Series("tpi", producing_t(ti, pairs["ai"].to_numpy(), cd)),
                               pl.Series("tpj", producing_t(tj, pairs["aj"].to_numpy(), cd)))
    cl = claims.select(pl.col("agent").alias("sender"), "message_id", pl.col("t").alias("tm"), "project", "pt_date")
    parts = []
    # claims of i that j could have seen at its switch call; claims of j that i could have seen
    for snd, rcv, ts, tsw, tpro in (("ai", "aj", "ti", "tj", "tpj"), ("aj", "ai", "tj", "ti", "tpi")):
        c = pairs.select("pid", "pt_date", "project", pl.col(snd).alias("sender"), pl.col(rcv).alias("rcv"),
                         pl.col(ts).alias("ts"), pl.col(tsw).alias("tsw"), pl.col(tpro).alias("tpro"))
        c = c.join(cl, on=["pt_date", "project", "sender"], how="inner")
        c = c.filter((pl.col("tm") >= pl.col("ts") - pl.duration(seconds=w_claim)) & (pl.col("tm") < pl.col("tsw")))
        parts.append(c)
    c = pl.concat(parts)
    if len(c):
        rr = rec.rename({"recipient": "rcv"}).with_columns(pl.col("rcv").cast(c.schema["rcv"]))
        c = c.join(rr, on=["message_id", "rcv"], how="left")
        c = c.with_columns((pl.col("t_recv").dt.epoch("us") <= pl.col("tpro")).fill_null(False).alias("seen"))
        g = c.group_by("pid").agg(pl.col("seen").any().alias("seen"), pl.len().alias("n_claims"))
    else:
        g = pl.DataFrame(schema={"pid": pairs.schema["pid"], "seen": pl.Boolean, "n_claims": pl.UInt32})
    pairs = pairs.join(g, on="pid", how="left").with_columns(
        pl.when(pl.col("seen").is_null()).then(pl.lit("silent")).when(pl.col("seen")).then(pl.lit("read"))
        .otherwise(pl.lit("inflight")).alias("cls"), pl.col("n_claims").fill_null(0))
    return pairs.drop("seen")


def departures(agent: np.ndarray, tstar_us: np.ndarray, day: np.ndarray, proj: np.ndarray, touches: pl.DataFrame,
               cd: dict, Ks=KS) -> dict:
    """For each row: departed within K calls (1/0) or -1 if censored."""
    out = {K: np.full(len(agent), -1, np.int8) for K in Ks}
    tt = {}
    for (a,), g in touches.group_by(["agent"], maintain_order=True):
        g = g.sort("t")
        tt[int(a)] = (g["t"].dt.epoch("us").to_numpy(), g["project"].to_numpy())
    for idx in range(len(agent)):
        a = int(agent[idx]); v = cd.get(a); w = tt.get(a)
        if v is None or w is None:
            continue
        ca, cdays = v
        k0 = np.searchsorted(ca, tstar_us[idx], side="right")
        tl, pr = w
        for K in Ks:
            kk = k0 + K  # index of the (K+1)-th call after t*: label = last touch before its t_call
            if kk >= len(ca) or cdays[kk] != day[idx]:
                continue
            end = ca[kk]
            p = np.searchsorted(tl, end, side="left") - 1
            lab = pr[p] if p >= 0 else None
            out[K][idx] = 0 if lab == proj[idx] else 1
    return out


def attach_departures(pairs: pl.DataFrame, touches: pl.DataFrame, cd: dict, Ks=KS) -> pl.DataFrame:
    if len(pairs) == 0:
        return pairs
    ts = pairs["tj"].dt.epoch("us").to_numpy()
    day = pairs["pt_date"].to_numpy(); proj = pairs["project"].to_numpy()
    di = departures(pairs["ai"].to_numpy(), ts, day, proj, touches, cd, Ks)
    dj = departures(pairs["aj"].to_numpy(), ts, day, proj, touches, cd, Ks)
    cols = []
    for K in Ks:
        cols += [pl.Series(f"dep_i_{K}", di[K]), pl.Series(f"dep_j_{K}", dj[K])]
    return pairs.with_columns(cols)


def solo_departures(solo: pl.DataFrame, touches: pl.DataFrame, cd: dict, shift_s: float, Ks=KS) -> pl.DataFrame:
    if len(solo) == 0:
        return solo
    ts = solo["t"].dt.epoch("us").to_numpy() + int(shift_s * US)
    d = departures(solo["agent"].to_numpy(), ts, solo["pt_date"].to_numpy(), solo["project"].to_numpy(), touches, cd, Ks)
    return solo.with_columns([pl.Series(f"dep_{K}", d[K]) for K in Ks])


def work_departures(pairs: pl.DataFrame, work: pl.DataFrame, horizon: float = WORK_HORIZON) -> pl.DataFrame:
    """Work channel: departed if the agent's next work commit after t* within `horizon` is on another repo; -1 if none."""
    tt = {}
    for (a,), g in work.group_by(["agent"], maintain_order=True):
        g = g.sort("t")
        tt[int(a)] = (g["t"].dt.epoch("us").to_numpy(), g["project"].to_numpy())
    ts = pairs["tj"].dt.epoch("us").to_numpy()
    res = {}
    for col in ("ai", "aj"):
        ag = pairs[col].to_numpy(); out = np.full(len(pairs), -1, np.int8)
        for i in range(len(pairs)):
            w = tt.get(int(ag[i]))
            if w is None:
                continue
            k = np.searchsorted(w[0], ts[i], side="right")
            if k < len(w[0]) and w[0][k] - ts[i] <= horizon * US:
                out[i] = 0 if w[1][k] == pairs["project"][i] else 1
        res[col] = out
    return pairs.with_columns(pl.Series("wdep_i", res["ai"]), pl.Series("wdep_j", res["aj"]))


def lag_bin(lag: pl.Expr) -> pl.Expr:
    return pl.when(lag < LAG_BINS[1]).then(0).when(lag < LAG_BINS[2]).then(1).otherwise(2).cast(pl.Int8)


def build_from_frames(touches, claims, rec, calls, named: dict | None = None, labs: dict | None = None,
                      Ks=KS) -> dict:
    cd = calls_dict(calls)
    sw = switch_ins(touches)
    pairs, solo = pair_switches(sw)
    pairs = classify(pairs, claims, rec, cd)
    pairs = attach_departures(pairs, touches, cd, Ks)
    med = float(pairs["lag"].median()) if len(pairs) else 60.0
    solo = solo_departures(solo, touches, cd, med, Ks)
    named = named or {}
    labs = labs or {}
    if len(pairs):
        pairs = pairs.with_columns(
            pl.col("project").map_elements(lambda p: bool(named.get(p, False)), return_dtype=pl.Boolean).alias("named"),
            lag_bin(pl.col("lag")).alias("lag_bin"),
            (pl.col("ai").map_elements(lambda a: labs.get(int(a), "?"), return_dtype=pl.String)
             == pl.col("aj").map_elements(lambda a: labs.get(int(a), "?"), return_dtype=pl.String)).alias("same_lab"))
    if len(solo):
        solo = solo.with_columns(
            pl.col("project").map_elements(lambda p: bool(named.get(p, False)), return_dtype=pl.Boolean).alias("named"))
    return {"switches": sw, "pairs": pairs, "solo": solo, "median_lag": med}


def build_period(goal_no: int, allow_holdout: bool = False, with_work: bool = True, days: list[str] | None = None) -> dict:
    """days: optional explicit day list (confirm.py: the #51 tail); held-out days are refused unless allow_holdout."""
    allowed = period_days(goal_no, allow_holdout)
    days = allowed if days is None else [d for d in days if d in allowed]
    touches = load_touches(goal_no, days)
    claims = load_claims(goal_no, days)
    calls = load_calls_period(goal_no, days)
    rec = load_receipts(claims["message_id"].unique().to_list(), days)
    from replicator_hosts import kickoff_named
    projs = touches["project"].unique().to_list()
    try:
        named = kickoff_named(goal_no, projs)
    except Exception:  # noqa: BLE001  (periods without kickoff text)
        named = {}
    ro = pl.read_parquet(SHARED / "roster.parquet", columns=["agent", "lab"])
    labs = {int(a): str(l) for a, l in ro.iter_rows()}
    out = build_from_frames(touches, claims, rec, calls, named, labs)
    out.update(days=days, n_touches=len(touches), n_claims=len(claims), n_calls=len(calls))
    if with_work:
        work = load_work(goal_no, days)
        wsw = switch_ins(work)
        wp, wsolo = pair_switches(wsw)
        cd = calls_dict(calls)
        wp = classify(wp, claims, rec, cd)
        if len(wp):
            wp = work_departures(wp, work).with_columns(lag_bin(pl.col("lag")).alias("lag_bin"),
                pl.col("project").map_elements(lambda p: bool(named.get(p, False)), return_dtype=pl.Boolean).alias("named"))
        out["work_pairs"] = wp
        out["n_work"] = len(work)
    return out


def hashed(df: pl.DataFrame, cols=("project",)) -> pl.DataFrame:
    for c in cols:
        if c in df.columns:
            df = df.with_columns(pl.col(c).map_elements(phash, return_dtype=pl.String))
    return df
