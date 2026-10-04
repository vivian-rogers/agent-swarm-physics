"""H04 round 1b (improved data, 2026-10-04): nudge and human-message kernels without future-kick isolation.

  uv run python hypotheses/H04-reversible-forcing/analysis/r1b.py                 # every suite
  uv run python hypotheses/H04-reversible-forcing/analysis/r1b.py --suite G51     # one suite

What changed from round 1 (`explore.py`, kept runnable and unchanged; it reads the round-1 table by default):
1. activity from `activity_bins_fixed.parquet` (DQ8: the old table dropped about half of all events);
2. a nudge's target is its **leading @** (H35; 29% of nudges also name other agents, who become bystanders), read from
   the message text in memory (never stored) with `common.mention_regexes`; fallback = the first parsed target;
3. **no future-kick isolation** (H30, H39, DQ8): every nudge is treated; controls are eligible on past information only
   (no direct kick to the agent at the control minute), future kicks are allowed in both arms, and the minutes since
   the agent's last direct kick are a matching stratum (so repeat nudges are matched to recently kicked controls);
4. a **day fixed effect**: each day's mean control residual δ_d(τ) is subtracted (additive day FE in the matching design);
5. a **presence mask**: cells outside the agent's first..last record of the day are excluded and trajectories are cut at
   the end of presence (DQ8: grid idle before/after presence fakes effects);
6. first vs repeat nudges (first = no direct kick to the agent in [m − 30, m − 1]; repeat = a nudge to it in
   [m − 60, m − 1]);
7. the dead time measured from the **receiving call**: the ledger's `age_s` of the nudge at the target's receiving call
   (`context_ledger_items`), kernels stratified by read-out delay, and the onset t25 (first minute at which the
   cumulative response reaches 25% of A30).
Direct kicks (eligibility, strata) = nudges to the agent (leading @) and human messages in its room (round-1 rule).
Outputs: data/processed/H04-reversible-forcing/r1b/<suite>.json (+ _provenance.json). Holdout days never loaded.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "2"
os.environ.setdefault("H04_ACTIVITY_TABLE", "activity_bins_fixed.parquet")

import argparse
import re
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h04lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import mention_regexes  # noqa: E402

OUTR = L.OUT / "r1b"
PRE, POST = 30, 60
LAGS = np.arange(-PRE, POST + 1)
L0 = PRE
HIST = 15
MIN_CTRL = 20
B = 1000
ACT_B = np.array([0, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3])
IDLE_B = np.array([0] + [1] * 7 + [2] * 8)
SINCE_ACT_EDGES = np.array([1, 5, 15, 30])        # minutes since last active minute: 0 | 1-4 | 5-14 | 15-29 | 30+ / never
SINCE_KICK_EDGES = np.array([16, 31, 61])          # minutes since last direct kick: 1-15 | 16-30 | 31-60 | none (> 60)
N_LOC = 4 * 4 * 3 * 5 * 4 * 3
RB_EDGES = [0, 60, 180, 600, 1e9]                  # read-out delay bins (s)
RB_LAB = ["le1m", "1to3m", "3to10m", "gt10m"]


# ----------------------------------------------------------------------------------------- kicks
_RX = None


def leading_target(text: str, valid: set[int]) -> int | None:
    """The agent named by the first @-mention (or first name match) in a nudge, restricted to that day's roster."""
    global _RX
    if _RX is None:
        ros = pl.read_parquet(L.S / "roster.parquet").select(pl.col("agent").alias("id"), "name").to_dicts()
        _RX = mention_regexes(ros)
    best, pos = None, 10 ** 9
    at = text.find("@")
    for a, rx in _RX.items():
        if a not in valid:
            continue
        m = rx.search(text, max(0, at) if at >= 0 else 0)
        if m and m.start() < pos:
            best, pos = a, m.start()
    return best


def load_kicks(days: list[str]) -> pl.DataFrame:
    """Nudges (leading-@ target, bystanders) and human messages (recipients, mentioned), from kicks_classified."""
    k = (pl.read_parquet(L.S / "kicks_classified.parquet").filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout")
                                                                  & pl.col("kind").cast(pl.Utf8).is_in(["nudge", "human_message"])))
    txt = pl.read_parquet(L.S / "chat_text.parquet", columns=["message_id", "text"]).filter(
        pl.col("message_id").is_in(k.filter(pl.col("kind").cast(pl.Utf8) == "nudge")["message_id"].implode()))
    tmap = dict(zip(txt["message_id"].to_list(), txt["text"].to_list()))
    lead = []
    for r in k.iter_rows(named=True):
        if r["kind"] == "nudge":
            tg = [int(x) for x in (r["targets"] or [])]
            lt = leading_target(tmap.get(r["message_id"]) or "", set(tg)) if tg else None
            lead.append(lt if lt is not None else (tg[0] if tg else None))
        else:
            lead.append(None)
    del tmap
    return k.with_columns(pl.Series("lead", lead, dtype=pl.Int8)).select(
        "t", "pt_date", "goal_no", pl.col("kind").cast(pl.Utf8), "message_id", "targets", "recipients", "lead")


def readout_delays(k: pl.DataFrame) -> pl.DataFrame:
    """Ledger read-out of each nudge at its leading target: age_s at the receiving call and that call's first record."""
    n = k.filter((pl.col("kind") == "nudge") & pl.col("lead").is_not_null()).select("message_id", "lead", "t")
    it = (pl.scan_parquet(L.S / "context_ledger_items.parquet").filter(pl.col("message_id").is_in(n["message_id"].implode()))
          .select("turn_id", "message_id", "age_s").collect())
    cw = (pl.scan_parquet(L.S / "call_windows.parquet").filter(pl.col("turn_id").is_in(it["turn_id"].implode()))
          .select("turn_id", "agent", "t_call", "t_first", "gap_kind", "wake_early").collect())
    it = it.join(cw, on="turn_id")
    out = n.join(it, left_on=["message_id", "lead"], right_on=["message_id", "agent"], how="left")
    return out.with_columns(((pl.col("t_first") - pl.col("t")).dt.total_microseconds() / 1e6).alias("first_rec_s"))


# ----------------------------------------------------------------------------------------- cells
def fsum(x: np.ndarray, lo: int, hi: int) -> np.ndarray:
    """Float-safe window sum of x[:, m+lo .. m+hi] (inclusive, truncated) for every m (fixes h04lib.window_sum's int64)."""
    n = x.shape[1]
    cs = np.concatenate([np.zeros((x.shape[0], 1)), np.cumsum(x, axis=1, dtype=np.float64)], axis=1)
    m = np.arange(n)
    return cs[:, np.clip(m + hi + 1, 0, n)] - cs[:, np.clip(m + lo, 0, n)]


class Suite:
    def __init__(self, days: list[str], var: str = "active"):
        self.days = days
        self.D = L.load_days(days)
        self.dix = {d.pt_date: k for k, d in enumerate(self.D)}
        self.kicks = load_kicks(days)
        self.var = var
        self._hits()
        self._cells()

    def _hits(self):
        for d in self.D:
            z = lambda: np.zeros(d.state.shape, dtype=np.int16)
            d.n_tgt, d.n_by, d.h_rec, d.h_men, d.dirk = z(), z(), z(), z(), z()
        self.treat = []   # (day, row, minute, kind, role, message_id)
        for r in self.kicks.iter_rows(named=True):
            k = self.dix.get(r["pt_date"])
            if k is None:
                continue
            d = self.D[k]
            m = int((r["t"] - d.win_start).total_seconds() // 60)
            if m < 0 or m >= d.n_min:
                continue
            rec = set(int(x) for x in (r["recipients"] or []))
            if r["kind"] == "nudge":
                tg = r["lead"]
                if tg is not None and d.row(tg) >= 0:
                    i = d.row(tg); d.n_tgt[i, m] += 1; d.dirk[i, m] += 1
                    self.treat.append((k, i, m, "nudge", "target", r["message_id"]))
                for a in rec | set(int(x) for x in (r["targets"] or [])):
                    if a == tg or d.row(a) < 0:
                        continue
                    i = d.row(a); d.n_by[i, m] += 1
                    self.treat.append((k, i, m, "nudge", "bystander", r["message_id"]))
            else:
                men = set(int(x) for x in (r["targets"] or []))
                for a in rec:
                    i = d.row(a)
                    if i < 0:
                        continue
                    d.h_rec[i, m] += 1; d.dirk[i, m] += 1
                    if a in men:
                        d.h_men[i, m] += 1
                    self.treat.append((k, i, m, "human", "mentioned" if a in men else "unmentioned", r["message_id"]))

    def _cells(self):
        P = {k: [] for k in ("day", "row", "minute", "agent", "sf", "sl", "elig", "traj", "first", "repeat")}
        for k, d in enumerate(self.D):
            st = d.state
            na, nm = st.shape
            if nm < HIST + 31:
                continue
            n = (st >= 3).astype(np.int8)
            y = n if self.var == "active" else (st == 4).astype(np.int8)
            idle = (st == 2).astype(np.int8)
            present_any = st != 1
            first = np.where(present_any.any(1), present_any.argmax(1), nm)
            last = np.where(present_any.any(1), nm - 1 - present_any[:, ::-1].argmax(1), -1)
            pres = (np.arange(nm)[None, :] >= first[:, None]) & (np.arange(nm)[None, :] <= last[:, None])
            m = np.arange(HIST, nm - 1)
            act15 = fsum(n, -HIST, -1)[:, m].astype(int)
            idl15 = fsum(idle, -HIST, -1)[:, m].astype(int)
            sprev = st[:, m - 1].astype(np.int64) - 1
            # minutes since the last active minute before m (0 if active at m-1; HIST.. capped)
            lastact = np.full((na, nm), -10 ** 6, np.int64)
            cur = np.full(na, -10 ** 6, np.int64)
            for t in range(nm):
                lastact[:, t] = cur
                cur = np.where(n[:, t] == 1, t, cur)
            since_a = m[None, :] - lastact[:, m]            # >= 1
            sa = np.digitize(since_a, SINCE_ACT_EDGES)       # 0: since=... careful: since 1 -> bin 1? (edges 1,5,15,30)
            sa = np.clip(sa - 0, 0, 4)
            # minutes since last direct kick strictly before m
            lastk = np.full((na, nm), -10 ** 6, np.int64)
            cur = np.full(na, -10 ** 6, np.int64)
            for t in range(nm):
                lastk[:, t] = cur
                cur = np.where(d.dirk[:, t] > 0, t, cur)
            since_k = m[None, :] - lastk[:, m]
            sk = np.digitize(since_k, SINCE_KICK_EDGES)      # 0: 1-15, 1: 16-30, 2: 31-60, 3: > 60 / none
            tod = (m * 3 // nm)[None, :].repeat(na, 0)
            loc = ((((sprev * 4 + ACT_B[act15]) * 3 + IDLE_B[idl15]) * 5 + sa) * 4 + sk) * 3 + tod
            aidx = d.agents.astype(np.int64)[:, None].repeat(len(m), 1)
            elig = pres[:, m] & (d.dirk[:, m] == 0) & (d.n_by[:, m] == 0)
            # trajectories, cut at the end of presence and the day
            yy = np.where(pres, y, -1).astype(np.int8)
            pad = np.full((na, PRE + nm + POST), -1, dtype=np.int8)
            pad[:, PRE:PRE + nm] = yy
            cols = PRE + m[:, None] + LAGS[None, :]
            traj = pad[:, cols]
            # pre-kick part before presence stays -1 (invalid); post-presence -1
            nmask = fsum(d.n_tgt.astype(float) + d.h_rec, -PRE, -1)[:, m]
            firstk = (fsum(d.dirk.astype(float), -30, -1)[:, m] == 0)
            repeat = (fsum(d.n_tgt.astype(float), -60, -1)[:, m] > 0)
            keep = pres[:, m]
            rr = np.arange(na)[:, None].repeat(len(m), 1)
            sel = keep.ravel()
            P["day"].append(np.full(sel.sum(), k, np.int32))
            P["row"].append(rr.ravel()[sel].astype(np.int16))
            P["minute"].append(np.tile(m, na)[sel].astype(np.int32))
            P["agent"].append(np.repeat(d.agents, len(m))[sel].astype(np.int16))
            P["sf"].append((aidx * N_LOC + loc).ravel()[sel])
            P["sl"].append(loc.ravel()[sel])
            P["elig"].append(elig.ravel()[sel])
            P["traj"].append(traj.reshape(-1, len(LAGS))[sel])
            P["first"].append(firstk.ravel()[sel])
            P["repeat"].append(repeat.ravel()[sel])
        for kk, v in P.items():
            setattr(self, kk, np.concatenate(v))
        self.index = {(int(a), int(b), int(c)): j for j, (a, b, c) in enumerate(zip(self.day, self.row, self.minute))}
        self.nd = len(self.D)
        self._controls()

    def _controls(self):
        e = self.elig
        tr = self.traj[e]
        nl = len(LAGS)
        uf, fi = np.unique(self.sf, return_inverse=True)
        ul, li = np.unique(self.sl, return_inverse=True)
        self.fi, self.li = fi, li
        mf = np.zeros((len(uf), nl)); kf = np.zeros((len(uf), nl))
        ml = np.zeros((len(ul), nl)); kl = np.zeros((len(ul), nl))
        fe, le = fi[e], li[e]
        for j in range(nl):
            v = tr[:, j] >= 0
            x = tr[:, j].astype(np.float64)
            kf[:, j] = np.bincount(fe[v], minlength=len(uf)); mf[:, j] = np.bincount(fe[v], weights=x[v], minlength=len(uf))
            kl[:, j] = np.bincount(le[v], minlength=len(ul)); ml[:, j] = np.bincount(le[v], weights=x[v], minlength=len(ul))
        with np.errstate(invalid="ignore", divide="ignore"):
            self.mf, self.ml = mf / kf, ml / kl
        self.kf = kf
        # control means for every cell; day FE = per-day mean residual of control-eligible cells
        cm = self.cmean(np.arange(len(self.day)))
        res = np.where((self.traj >= 0) & np.isfinite(cm), self.traj - np.nan_to_num(cm), np.nan)
        dsum = np.zeros((self.nd, nl)); dcnt = np.zeros((self.nd, nl))
        r_e = res[e]; d_e = self.day[e]
        for j in range(nl):
            v = np.isfinite(r_e[:, j])
            np.add.at(dsum[:, j], d_e[v], r_e[v, j]); np.add.at(dcnt[:, j], d_e[v], 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            self.delta = np.nan_to_num(dsum / dcnt)
        self._cm_all = cm

    def cmean(self, ids):
        use_f = self.kf[self.fi[ids], L0 + 1] >= MIN_CTRL
        return np.where(use_f[:, None], self.mf[self.fi[ids]], self.ml[self.li[ids]])

    def lookup(self, rows):
        return np.array([self.index.get((k, i, m), -1) for k, i, m in rows], np.int64)

    def response(self, ids: np.ndarray, day_fe: bool = True, shift: np.ndarray | None = None) -> dict:
        """Per-day sums of treated - matched control (- day FE) trajectories."""
        ids = ids[ids >= 0]
        nl = len(LAGS)
        if len(ids) == 0:
            return None
        cm = self._cm_all[ids]
        tr = self.traj[ids].astype(float)
        valid = (self.traj[ids] >= 0) & np.isfinite(cm)
        res = np.where(valid, tr - np.nan_to_num(cm) - (self.delta[self.day[ids]] if day_fe else 0.0), 0.0)
        dd = self.day[ids]
        ds = np.zeros((self.nd, nl)); dc = np.zeros((self.nd, nl))
        np.add.at(ds, dd, res); np.add.at(dc, dd, valid.astype(float))
        return {"ds": ds, "dc": dc, "n": int(len(ids)), "fallback": float(1 - (self.kf[self.fi[ids], L0 + 1] >= MIN_CTRL).mean())}


def summarize(r: dict | None, W: np.ndarray) -> dict:
    if r is None:
        return {"n_cells": 0}
    with np.errstate(invalid="ignore", divide="ignore"):
        G = (W @ r["ds"]) / (W @ r["dc"])
    out = {"n_cells": r["n"], "n_days": int((r["dc"][:, L0 + 1] > 0).sum()), "fallback_share": r["fallback"]}
    for lab, (lo, hi) in {"A30": (1, 30), "A60": (1, 60), "A5": (1, 5), "A6_30": (6, 30), "placebo_m30_m16": (-30, -16),
                          "pre_m15_m1": (-15, -1)}.items():
        out[lab] = L.ci(np.nansum(G[:, L0 + lo:L0 + hi + 1], axis=1))
    with np.errstate(invalid="ignore", divide="ignore"):   # H08's onset fraction: Phi(a, b) = mean G[a..b] / mean G[16..45]
        late = np.nanmean(G[:, L0 + 16:L0 + 46], axis=1)
        out["Phi_1_5"] = L.ci(np.nanmean(G[:, L0 + 1:L0 + 6], axis=1) / late)
        out["Phi_6_15"] = L.ci(np.nanmean(G[:, L0 + 6:L0 + 16], axis=1) / late)
    g0 = G[0]
    cum = np.nancumsum(g0[L0 + 1:L0 + 31])
    a30 = cum[-1]
    out["t25"] = int(np.argmax(cum >= 0.25 * a30) + 1) if a30 > 0 and (cum >= 0.25 * a30).any() else None
    out["t50"] = int(np.argmax(cum >= 0.5 * a30) + 1) if a30 > 0 and (cum >= 0.5 * a30).any() else None
    t25b = []
    for g in G[1:]:
        c = np.nancumsum(g[L0 + 1:L0 + 31])
        t25b.append(np.argmax(c >= 0.25 * c[-1]) + 1 if c[-1] > 0 and (c >= 0.25 * c[-1]).any() else np.nan)
    out["t25_ci"] = [float(np.nanpercentile(t25b, 2.5)), float(np.nanpercentile(t25b, 97.5))] if np.isfinite(t25b).sum() > 20 else None
    out.update(L.shape_stats(g0))
    out["G"] = [None if not np.isfinite(x) else round(float(x), 5) for x in g0]
    lo, hi = np.nanpercentile(G[1:], [2.5, 97.5], axis=0)
    out["G_lo"] = [None if not np.isfinite(x) else round(float(x), 5) for x in lo]
    out["G_hi"] = [None if not np.isfinite(x) else round(float(x), 5) for x in hi]
    return out


def run_suite(label: str, days: list[str], B_: int = B, readout: bool = True, humans: bool = True) -> dict:
    t0 = time.time()
    S = Suite(days)
    W = L.boot_weights(S.nd, B_)
    T = pl.DataFrame(S.treat, schema=["day", "row", "minute", "kind", "role", "message_id"], orient="row")
    out = {"label": label, "n_days": S.nd, "date_range": [days[0], days[-1]], "activity_table": L.ACTIVITY_TABLE,
           "n_nudges": int(S.kicks.filter(pl.col("kind") == "nudge").height),
           "n_nudges_multi_target": int(S.kicks.filter((pl.col("kind") == "nudge") & (pl.col("targets").list.len() > 1)).height),
           "n_human": int(S.kicks.filter(pl.col("kind") == "human_message").height), "n_cells": int(len(S.day)),
           "control_eligible_share": float(S.elig.mean())}
    sets = {}

    def ids_of(df):
        df = df.unique(["day", "row", "minute"], maintain_order=True)
        return S.lookup(df.select("day", "row", "minute").iter_rows()), df
    tg, tgdf = ids_of(T.filter((pl.col("kind") == "nudge") & (pl.col("role") == "target")))
    sets["nudge_target_all"] = tg
    ok = tg >= 0
    first = np.zeros(len(tg), bool); rep = np.zeros(len(tg), bool)
    first[ok] = S.first[tg[ok]]; rep[ok] = S.repeat[tg[ok]]
    sets["nudge_target_first"] = tg[first]
    sets["nudge_target_repeat"] = tg[rep]
    sets["nudge_target_notfirst"] = tg[ok & ~first]
    sets["nudge_bystander"] = ids_of(T.filter((pl.col("kind") == "nudge") & (pl.col("role") == "bystander")))[0]
    if humans:
        sets["human_all"] = ids_of(T.filter(pl.col("kind") == "human"))[0]
        sets["human_mentioned"] = ids_of(T.filter((pl.col("kind") == "human") & (pl.col("role") == "mentioned")))[0]
        sets["human_unmentioned"] = ids_of(T.filter((pl.col("kind") == "human") & (pl.col("role") == "unmentioned")))[0]
    out["G"] = {}
    for name, ids in sets.items():
        out["G"][name] = summarize(S.response(ids, day_fe=True), W)
        if name.startswith("nudge_target") or name == "human_mentioned":
            out["G"][name + "_noDayFE"] = summarize(S.response(ids, day_fe=False), W)
            out["G"][name + "_noDayFE"].pop("G", None)
    # first - repeat contrast
    rf, rr = S.response(sets["nudge_target_first"]), S.response(sets["nudge_target_repeat"])
    if rf and rr:
        with np.errstate(invalid="ignore", divide="ignore"):
            gf = (W @ rf["ds"]) / (W @ rf["dc"]); gr = (W @ rr["ds"]) / (W @ rr["dc"])
        out["first_minus_repeat_A30"] = L.ci(np.nansum(gf[:, L0 + 1:L0 + 31], 1) - np.nansum(gr[:, L0 + 1:L0 + 31], 1))
    # round-1 isolation rule inside the round-1b estimator (for the inflation check): no other direct kick in [m-30, m+60]
    iso = []
    for j in sets["nudge_target_all"]:
        if j < 0:
            continue
        k, i, m = int(S.day[j]), int(S.row[j]), int(S.minute[j])
        dk = S.D[k].dirk[i]
        if dk[max(0, m - 30):m].sum() == 0 and dk[m + 1:m + 61].sum() == 0:
            iso.append(j)
    out["G"]["nudge_target_r1isolated"] = summarize(S.response(np.array(iso, np.int64)), W)
    out["G"]["nudge_target_r1isolated"].pop("G", None)
    # read-out (receiving call) for nudges
    if readout:
        ro = readout_delays(S.kicks)
        out["readout"] = {"n": ro.height, "n_matched": int(ro["age_s"].is_not_null().sum())}
        rv = ro["age_s"].drop_nulls().to_numpy()
        if len(rv):
            out["readout"]["age_s_q"] = [float(x) for x in np.percentile(rv, [10, 25, 50, 75, 90])]
            fr = ro["first_rec_s"].drop_nulls().to_numpy()
            out["readout"]["first_rec_s_q"] = [float(x) for x in np.percentile(fr, [10, 25, 50, 75, 90])]
            out["readout"]["share_wake_early"] = float(ro["wake_early"].drop_nulls().mean() or 0)
            out["readout"]["gap_kind"] = {str(k_): int(v) for k_, v in ro.group_by("gap_kind").len().iter_rows()}
            # kernels by read-out delay bin (target cells)
            mid = dict(zip(ro["message_id"].to_list(), ro["age_s"].to_list()))
            tt = T.filter((pl.col("kind") == "nudge") & (pl.col("role") == "target"))
            ages = np.array([mid.get(x) if mid.get(x) is not None else np.nan for x in tt["message_id"].to_list()], float)
            ids_all = S.lookup(tt.select("day", "row", "minute").iter_rows())
            # zero-parameter read-out prediction of the onset (H08 C8, plain step, no headroom weighting):
            # tau_r = minute (relative to the kick minute) of the receiving call; F(tau) = P(tau_r <= tau)
            tk = dict(zip(S.kicks["message_id"].to_list(), S.kicks["t"].to_list()))
            taur = []
            for (k_, i_, m_, mid_), a_ in zip(tt.select("day", "row", "minute", "message_id").iter_rows(), ages):
                if not np.isfinite(a_):
                    continue
                sec = (tk[mid_] - S.D[k_].win_start).total_seconds() - 60 * m_
                taur.append(int((sec + a_) // 60))
            taur = np.array(taur)
            F = np.array([(taur <= x).mean() for x in range(0, 46)])
            out["readout"]["Phi_pred_step_1_5"] = float(F[1:6].mean() / F[16:46].mean())
            out["readout"]["Phi_pred_step_6_15"] = float(F[6:16].mean() / F[16:46].mean())
            out["readout"]["F_readout"] = F.round(4).tolist()
            out["by_readout"] = {}
            for lab, lo, hi in zip(RB_LAB, RB_EDGES[:-1], RB_EDGES[1:]):
                sel = (ages >= lo) & (ages < hi) & (ids_all >= 0)
                sm = summarize(S.response(ids_all[sel]), W)
                sm["median_readout_s"] = float(np.nanmedian(ages[sel])) if sel.any() else None
                out["by_readout"][lab] = sm
            # kernel re-aligned on the receiving call: shift each trajectory by the read-out minute offset
            okm = np.isfinite(ages) & (ids_all >= 0)
            offs = np.floor(ages[okm] / 60).astype(int)
            idsr = ids_all[okm]
            nl = len(LAGS)
            ds = np.zeros((S.nd, nl)); dc = np.zeros((S.nd, nl))
            cm = S._cm_all[idsr]; trj = S.traj[idsr].astype(float)
            val = (S.traj[idsr] >= 0) & np.isfinite(cm)
            res = np.where(val, trj - np.nan_to_num(cm) - S.delta[S.day[idsr]], np.nan)
            for q in range(len(idsr)):
                sh = offs[q]
                rr_ = np.full(nl, np.nan)
                if sh < nl:
                    rr_[:nl - sh] = res[q, sh:]
                v = np.isfinite(rr_)
                ds[S.day[idsr[q]], v] += rr_[v]; dc[S.day[idsr[q]], v] += 1
            out["G"]["nudge_target_readout_aligned"] = summarize({"ds": ds, "dc": dc, "n": int(len(idsr)), "fallback": np.nan}, W)
            out["G"]["nudge_target_readout_aligned"]["note"] = "lag 0 = the minute containing the receiving call's t_call"
    out["runtime_s"] = round(time.time() - t0, 1)
    return out


def suites(cal: pl.DataFrame) -> dict[str, list[str]]:
    def g(goals, d0=None, d1=None):
        c = cal.filter(pl.col("goal_no").is_in(goals) & (pl.col("window_s") > 0) & ~pl.col("holdout"))
        if d0:
            c = c.filter(pl.col("pt_date") >= d0)
        if d1:
            c = c.filter(pl.col("pt_date") < d1)
        days = sorted(c["pt_date"].to_list())
        assert not any(L.is_holdout_date(d, gg) for d, gg in c.select("pt_date", "goal_no").iter_rows())
        return days
    s = {f"G{x}": g([x]) for x in (35, 36, 37, 38, 39, 40, 41, 42, 44, 51)}
    s["III_4h_pre_NE44"] = g([36, 37, 38, 39, 40, 41, 42, 44], d0="2026-03-24")
    s["NE10_G30_G31"] = g([30, 31])
    s["NE43_pre"] = g([51], "2026-07-21", "2026-08-05")
    s["NE43_on"] = g([51], "2026-08-05", "2026-08-21")
    s["NE43_off"] = g([51], "2026-08-21", "2026-09-05")
    s["I_humans"] = sorted(cal.filter((pl.col("regime").cast(pl.Utf8) == "I") & (pl.col("window_s") > 0) & ~pl.col("holdout")
                                      & (pl.col("pt_date") >= "2025-12-20"))["pt_date"].to_list())
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", action="append")
    ap.add_argument("--boot", type=int, default=B)
    a = ap.parse_args()
    cal = L.calendar()
    S = suites(cal)
    OUTR.mkdir(parents=True, exist_ok=True)
    for name in (a.suite or list(S)):
        days = S[name]
        if not days:
            continue
        res = run_suite(name, days, a.boot, readout=not name.startswith("I_"), humans=True)
        L.jdump(res, OUTR / f"{name}.json")
        g = res["G"]
        f = lambda k: (g.get(k) or {}).get("A30")
        print(f"{name}: {res['n_days']} d, nudges {res['n_nudges']} | target A30 {f('nudge_target_all')} first {f('nudge_target_first')} "
              f"repeat {f('nudge_target_repeat')} r1iso {f('nudge_target_r1isolated')} | readout {res.get('readout', {}).get('age_s_q')} "
              f"| {res['runtime_s']}s", flush=True)
    prov_p = OUTR / "_provenance.json"
    import json, datetime as dt
    prov = {"built_by": "hypotheses/H04-reversible-forcing/analysis/r1b.py", "git_commit": L.git_commit(),
            "inputs": [{"source": "data/processed/shared (ai-village rev 838b4150303ca8228e8edb432d8b8ccae353d258)",
                        "tables": ["activity_bins_fixed", "kicks_classified", "chat_text (leading @, in memory only)",
                                   "context_ledger_items", "call_windows", "calendar", "roster"]}],
            "params": {"B": a.boot, "strata": "agent x state(m-1) x act15 x idle15 x since-active x since-direct-kick x day-third",
                       "eligibility": "past only (no direct kick or bystander nudge at m)", "day_fe": "additive (per-day mean control residual)",
                       "presence_mask": True, "first": "no direct kick in [m-30, m-1]", "repeat": "nudge in [m-60, m-1]",
                       "holdout": "never loaded"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_p.write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
