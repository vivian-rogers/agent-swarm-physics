"""H41 round 2, R2: ordered reads of the source's artifacts by cross-room adopters (case-control within items).

  uv run python hypotheses/H41-readout-light-cone/analysis/r2_reads.py build [--only 38]   # strata + flags per period
  uv run python hypotheses/H41-readout-light-cone/analysis/r2_reads.py synth                # Z0-Z3 worlds (size, power)
  uv run python hypotheses/H41-readout-light-cone/analysis/r2_reads.py real                 # statistics on real labels

Definitions: README "Round 2", R2 (written 2026-10-05 03:50 UTC, before any round-2 statistic).
Inputs: round-1b adoptions (G<NN>/adoptions.parquet), r2/tables (scheme/build_r2.py), shared chat artifact mentions,
call_windows via h41core.load_skeleton (reserved days removed). Outputs: data/processed/H41-readout-light-cone/r2/R2_*.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
import h41core as C  # noqa: E402

OUT = C.OUT / "r2"
TAB = OUT / "tables"
PERIODS_MAIN = [35, 36, 38, 42, 51]
PERIODS_DESC = [37, 39, 41, 44]
W_BACK = 6 * 3600.0
DBIN_EDGES = np.array([300.0, 1800.0, 7200.0, 8 * 3600.0, 24 * 3600.0])
B_REAL = 400
B_SYN = 200


def qci(v) -> tuple:
    """Percentile 95% interval that tolerates infinite draws (no-event denominators)."""
    v = np.asarray(v, float)
    v = v[~np.isnan(v)]
    if len(v) < 20:
        return (np.nan, np.nan)
    w = np.clip(v, -1e12, 1e12)
    lo, hi = np.quantile(w, .025), np.quantile(w, .975)
    f = lambda x: float(np.inf if x >= 1e11 else (-np.inf if x <= -1e11 else x))
    return (f(lo), f(hi))


# ============================================================================================ time helpers
class ActiveClock:
    def __init__(self, cal: pl.DataFrame, days: list):
        c = cal.filter(pl.col("pt_date").is_in(days)).sort("pt_date")
        self.off = c["active_offset_s"].to_numpy().astype(float)
        self.ws = c["ws"].to_numpy()
        self.wl = c["window_s"].to_numpy().astype(float)
        self.days = c["pt_date"].to_list()
        self.cal = cal
        self.end = float(self.off[-1] + self.wl[-1])

    def at(self, t: np.ndarray, days) -> np.ndarray:
        return C.active_time(np.asarray(t, float), np.asarray(days), self.cal)

    def wall(self, A: float) -> float:
        """Inverse of the active coordinate on the period's non-reserved days (clipped to day windows)."""
        i = int(np.searchsorted(self.off, A, side="right") - 1)
        i = min(max(i, 0), len(self.off) - 1)
        return float(self.ws[i] + min(max(A - self.off[i], 0.0), self.wl[i]))


# ============================================================================================ build
def load_tables():
    reads = pl.read_parquet(TAB / "reads.parquet")
    local = pl.read_parquet(TAB / "local_reads.parquet")
    cf = pl.read_parquet(TAB / "commit_files.parquet")
    wp = pl.read_parquet(TAB / "writes_push.parquet")
    art = pl.read_parquet(C.SH / "artifacts.parquet", columns=["artifact", "kind", "parent"]).with_columns(
        pl.col("kind").cast(pl.Utf8))
    parent = dict(zip(art["artifact"].to_list(), art["parent"].to_list()))
    kind = dict(zip(art["artifact"].to_list(), art["kind"].to_list()))
    chat_am = (pl.scan_parquet(C.SH / "artifact_mentions.parquet").filter(pl.col("source").cast(pl.Utf8) == "chat")
               .select("message_id", "artifact").collect())
    m0_links = {}
    for mid, a in zip(chat_am["message_id"].to_list(), chat_am["artifact"].to_list()):
        m0_links.setdefault(mid, set()).add(a)
    return reads, local, cf, wp, parent, kind, m0_links


def per_agent(df: pl.DataFrame, cols: list) -> dict:
    """Per-agent numpy columns; null ids become sentinels (repo -1, hashes 0) so int64 hashes keep full precision."""
    fill = {"repo": -1, "path_hash": 0, "base_hash": 0}
    df = df.with_columns([pl.col(c).fill_null(v) for c, v in fill.items() if c in df.columns])
    out = {}
    for (a,), sub in df.sort("agent", "t").group_by(["agent"], maintain_order=True):
        out[int(a)] = {c: sub[c].to_numpy() for c in cols}
    return out


class Writes:
    """Source writes in [lo, hi): min write time per match key."""

    def __init__(self, cf_s: dict, wp_s: dict, links: set, t_link: float, lo: float, hi: float, parent: dict, kind: dict):
        self.repo, self.site, self.fart, self.path, self.base = {}, {}, {}, {}, {}

        def put(d, k, t):
            if k is None:
                return
            if t < d.get(k, np.inf):
                d[k] = t

        if cf_s is not None:
            m = (cf_s["t"] >= lo) & (cf_s["t"] < hi)
            for r, p, b, bok, t in zip(cf_s["repo"][m], cf_s["path_hash"][m], cf_s["base_hash"][m], cf_s["base_ok"][m],
                                       cf_s["t"][m]):
                put(self.repo, int(r), t)
                if p != 0:
                    put(self.path, (int(r), int(p)), t)
                    if bok:
                        put(self.base, (int(r), int(b)), t)
        if wp_s is not None:
            m = (wp_s["t"] >= lo) & (wp_s["t"] < hi)
            for a, k, t in zip(wp_s["artifact"][m], wp_s["kind"][m], wp_s["t"][m]):
                a = int(a)
                if k == "repo":
                    put(self.repo, a, t)
                elif k == "site":
                    put(self.site, a, t)
                else:
                    put(self.fart, a, t)
        if lo <= t_link < hi:
            for a in links:
                k = kind.get(a)
                if k == "repo":
                    put(self.repo, int(a), t_link)
                elif k == "site":
                    put(self.site, int(a), t_link)
                elif k == "file":
                    put(self.fart, int(a), t_link)
        self.parent = parent
        self.empty = not (self.repo or self.site or self.fart or self.path)

    def tw_read(self, art: int, kind: str, repo, path_hash) -> float:
        """Earliest write time that a read of this artifact matches (inf if none)."""
        t = np.inf
        if kind == "repo":
            t = self.repo.get(art, np.inf)
        elif kind == "site":
            t = min(self.site.get(art, np.inf), self.repo.get(self.parent.get(art), np.inf))
        elif kind == "file":
            t = min(self.fart.get(art, np.inf), self.repo.get(repo, np.inf) if repo is not None else np.inf)
        return t

    def tw_local(self, repo: int, ph: int, match: str) -> float:
        return (self.path if match == "path" else self.base).get((repo, ph), np.inf)


def scan_reads(R: dict | None, L: dict | None, W: Writes, lo: float, hi: float, need_after_tw: bool = True):
    """Matching reads in (lo, hi). Returns (any, channels set, n_other_reads)."""
    hit, chans, n_other = False, set(), 0
    if R is not None:
        i0, i1 = np.searchsorted(R["t"], lo, side="right"), np.searchsorted(R["t"], hi, side="left")
        for j in range(i0, i1):
            rp = int(R["repo"][j])
            ph = int(R["path_hash"][j])
            tw = W.tw_read(int(R["artifact"][j]), R["kind"][j], None if rp < 0 else rp, ph)
            if tw < R["t"][j]:
                hit = True
                ch = R["chan"][j]
                if R["kind"][j] == "file" and ph != 0 and rp >= 0 and (rp, ph) in W.path:
                    ch = "file"
                chans.add(ch)
            else:
                n_other += 1
    if L is not None:
        i0, i1 = np.searchsorted(L["t"], lo, side="right"), np.searchsorted(L["t"], hi, side="left")
        for j in range(i0, i1):
            tw = W.tw_local(int(L["repo"][j]), int(L["path_hash"][j]), L["match"][j])
            if tw < L["t"][j]:
                hit = True
                chans.add("file")
    return hit, chans, n_other


def build_period(goal: int, tabs) -> dict:
    t_a = time.time()
    reads, local, cf, wp, parent, kind, m0_links = tabs
    cal = C.calendar()
    sk = C.load_skeleton(goal, cal)
    ri = C.RoomIndex(sk)
    clk = ActiveClock(cal, sk.days)
    adf = pl.read_parquet(C.OUT / f"G{goal:02d}/adoptions.parquet")
    msg_id = sk.msgs["message_id"].to_list()
    users = {}
    for mk, a in zip(adf["marker"].to_list(), adf["agent"].to_list()):
        users.setdefault(mk, set()).add(int(a))
    t_lo, t_hi = sk.t_min - 2 * 86400, sk.t_max + 86400
    R_by = per_agent(reads.filter((pl.col("t") >= t_lo) & (pl.col("t") <= t_hi)),
                     ["t", "artifact", "kind", "chan", "repo", "path_hash"])
    L_by = per_agent(local.filter((pl.col("t") >= t_lo) & (pl.col("t") <= t_hi)), ["t", "repo", "path_hash", "match"])
    cf_by = per_agent(cf.filter((pl.col("t") >= t_lo) & (pl.col("t") <= t_hi)).rename({"author_agent": "agent"}),
                      ["t", "repo", "path_hash", "base_hash", "base_ok"])
    wp_by = per_agent(wp.filter((pl.col("t") >= t_lo) & (pl.col("t") <= t_hi)), ["t", "artifact", "kind"])
    # per-agent talk calls and call lengths
    talk_t, talk_len, recv_t = {}, {}, {}
    for a, s in sk.agent_calls.items():
        ct = sk.c_t[s]
        ln = np.r_[np.diff(ct), 0.0]
        ln = np.clip(ln, 0, 1800.0)
        tk = sk.c_talk[s].astype(bool)
        talk_t[a], talk_len[a], recv_t[a] = ct[tk], ln[tk], ct
    # project propensity: reads of any repo the source committed to in the period, per active hour of the reader
    act_h = {a: max(len(v), 1) for a, v in recv_t.items()}
    proj_cache = {}

    def proj_rate(src, b):
        k = (src, b)
        if k in proj_cache:
            return proj_cache[k]
        c = cf_by.get(src)
        R = R_by.get(b)
        v = 0.0
        if c is not None and R is not None:
            rs = set(int(x) for x in c["repo"])
            v = float(sum(1 for r in R["repo"] if int(r) in rs))
        proj_cache[k] = v / act_h.get(b, 1)
        return proj_cache[k]

    known = (adf["room_t0"] >= 0) & (adf["room0"] >= 0)
    viol = adf.filter(known & pl.col("cross") & ~pl.col("in_cone_len") & (pl.col("src") >= 0) & (pl.col("src") < 64))
    inc = adf.filter(pl.col("in_cone") & pl.col("exposed") & (pl.col("src") >= 0) & (pl.col("src") < 64))
    rows, rows_ic = [], []
    agents_arr = np.array(sorted(int(a) for a in sk.agents))

    def flags(src, b, t0, t_use, at0, atu, m0, day0):
        W = Writes(cf_by.get(src), wp_by.get(src), m0_links.get(msg_id[m0], set()), t0, t0 - W_BACK, t_use, parent, kind)
        R, L = R_by.get(b), L_by.get(b)
        e_full, ch_full, n_oth = scan_reads(R, L, W, t0, t_use)
        e_minus, _, _ = scan_reads(R, L, W, t0 - W_BACK, t_use)
        dlt = atu - at0
        dl2 = min(dlt, clk.end - atu)
        dl2 = max(dl2, 0.0)
        pre_lo = clk.wall(atu - dl2) if dl2 < dlt else t0
        post_hi = clk.wall(atu + dl2)
        e_eq, _, _ = scan_reads(R, L, W, max(pre_lo, t0), t_use)
        e_post, _, _ = scan_reads(R, L, W, t_use, post_hi)
        tt = talk_t.get(b, np.array([]))
        m = (tt > t0) & (tt <= t_use)
        return dict(E_ord=e_full, E_ord_minus=e_minus, E_ord_eq=e_eq, E_post=e_post, E_other=n_oth > 0, n_other=n_oth,
                    ch_pull="pull" in ch_full, ch_page="page" in ch_full, ch_file="file" in ch_full, ch_api="api" in ch_full,
                    w_talk=int(m.sum()), w_len=float(talk_len.get(b, np.array([]))[m].sum()) if m.any() else 0.0,
                    w_proj=proj_rate(src, b), delta_act=dlt, delta_eq=dl2, writes_empty=W.empty)

    for k, x in enumerate(viol.iter_rows(named=True)):
        src, a, t0, t_use, mk, m0 = int(x["src"]), int(x["agent"]), x["t0"], x["t_use"], x["marker"], int(x["m0"])
        at0, atu = clk.at(np.array([t0, t_use]), np.array([x["day0"], x["day_use"]]))
        room0 = int(x["room0"])
        sid = f"{goal}:{k}"
        hour = int((t0 - sk.cal.filter(pl.col('pt_date') == x['day0'])['ws'][0]) // 3600) if x["day0"] in sk.days else 0
        clus = f"{goal}:{x['day0']}:{hour}"
        members = [(a, True)]
        for b in agents_arr:
            b = int(b)
            if b in (a, src) or b in users.get(mk, set()):
                continue
            rb = ri.at(b, t0)
            if rb < 0 or rb == room0:
                continue
            rt = recv_t.get(b)
            if rt is None or not np.any((rt > t0) & (rt <= t_use)):
                continue
            members.append((b, False))
        for b, is_ad in members:
            f = flags(src, b, t0, t_use, at0, atu, m0, x["day0"])
            rows.append(dict(goal=goal, sid=sid, clus=clus, marker=mk, cls=int(x["cls"]), src=src, agent=b, adopter=is_ad,
                             t0=t0, t_use=t_use, delay=t_use - t0, n_members=len(members), **f))
    for x in inc.iter_rows(named=True):
        src, a, t0, t_use, m0 = int(x["src"]), int(x["agent"]), x["t0"], x["t_use"], int(x["m0"])
        W = Writes(cf_by.get(src), wp_by.get(src), m0_links.get(msg_id[m0], set()), t0, t0 - W_BACK, t_use, parent, kind)
        e, ch, _ = scan_reads(R_by.get(a), L_by.get(a), W, t0, t_use)
        rows_ic.append(dict(goal=goal, marker=x["marker"], cls=int(x["cls"]), agent=a, cross=bool(x["cross"]),
                            delay=t_use - t0, E_ord=e, writes_empty=W.empty))
    df = pl.DataFrame(rows, infer_schema_length=None) if rows else pl.DataFrame()
    dic = pl.DataFrame(rows_ic, infer_schema_length=None) if rows_ic else pl.DataFrame()
    od = OUT / "R2"
    od.mkdir(parents=True, exist_ok=True)
    if df.height:
        df.write_parquet(od / f"members_G{goal:02d}.parquet", compression="zstd")
    if dic.height:
        dic.write_parquet(od / f"incone_G{goal:02d}.parquet", compression="zstd")
    meta = dict(goal=goal, n_strata=viol.height, n_rows=df.height, n_incone=dic.height, secs=round(time.time() - t_a, 1))
    print(meta, flush=True)
    return meta


# ============================================================================================ statistics
def mh_or(case: np.ndarray, exp: np.ndarray, strata: np.ndarray) -> float:
    """Mantel-Haenszel odds ratio of a binary exposure, case vs control, over strata (vectorized; integer strata)."""
    _, s = np.unique(strata, return_inverse=True)
    k = s.max() + 1 if len(s) else 0
    n = np.bincount(s, minlength=k).astype(float)
    A = np.bincount(s, weights=(case & exp), minlength=k)
    Bc = np.bincount(s, weights=(case & ~exp), minlength=k)
    Cc = np.bincount(s, weights=(~case & exp), minlength=k)
    D = np.bincount(s, weights=(~case & ~exp), minlength=k)
    nc = A + Bc
    ok = (n >= 2) & (nc > 0) & (nc < n)
    num = float(np.sum(A[ok] * D[ok] / n[ok]))
    den = float(np.sum(Bc[ok] * Cc[ok] / n[ok]))
    if den == 0:
        return np.inf if num > 0 else np.nan
    return num / den


class Arr:
    """Numpy view of the member table for fast resampling."""

    def __init__(self, df: pl.DataFrame, case_col: str = "adopter"):
        self.case = df[case_col].to_numpy().astype(bool)
        _, self.sid = np.unique(df["sid"].to_numpy(), return_inverse=True)
        self.E = {c: df[c].to_numpy().astype(bool) for c in ["E_ord", "E_ord_eq", "E_post", "E_other"]}
        _, self.cl = np.unique(df["clus"].to_numpy(), return_inverse=True)

    def take(self, ii: np.ndarray, sid_new: np.ndarray):
        o = Arr.__new__(Arr)
        o.case = self.case[ii]
        o.sid = sid_new
        o.E = {k: v[ii] for k, v in self.E.items()}
        return o


def lam_arr(a: Arr) -> dict:
    o1 = mh_or(a.case, a.E["E_ord_eq"], a.sid)
    o2 = mh_or(a.case, a.E["E_post"], a.sid)
    of = mh_or(a.case, a.E["E_ord"], a.sid)
    oo = mh_or(a.case, a.E["E_other"], a.sid)
    lam = o1 / o2 if (np.isfinite(o1) and np.isfinite(o2) and o2 > 0) else (np.inf if (np.isfinite(o1) and o1 > 0 and o2 == 0) else np.nan)
    spec = of / oo if (np.isfinite(of) and np.isfinite(oo) and oo > 0) else np.nan
    return dict(OR_ord=of, OR_ord_eq=o1, OR_post=o2, Lambda=lam, OR_other=oo, spec=spec)


def lam_stats(df: pl.DataFrame, case_col: str = "adopter") -> dict:
    return lam_arr(Arr(df, case_col))


def boot_arr(a: Arr, B: int, seed: int = 0, keys=("Lambda",)) -> dict:
    """Cluster bootstrap (1-h blocks of t0 within PT days); resampled clusters get new stratum ids."""
    ncl = a.cl.max() + 1
    idx = [np.flatnonzero(a.cl == c) for c in range(ncl)]
    nsid = a.sid.max() + 1
    rng = np.random.default_rng(seed)
    out = {k: [] for k in keys}
    for _ in range(B):
        pick = rng.integers(0, ncl, ncl)
        ii = np.concatenate([idx[p] for p in pick])
        rep = np.repeat(np.arange(ncl), [len(idx[p]) for p in pick])
        r = lam_arr(a.take(ii, a.sid[ii] + nsid * rep))
        for k in keys:
            out[k].append(r[k])
    res = {}
    for k in keys:
        v = np.array(out[k], float)
        res[k + "_ci"] = qci(v)
    return res


def boot(df: pl.DataFrame, fn=None, B: int = 400, seed: int = 0, keys=("Lambda",), case_col: str = "adopter") -> dict:
    return boot_arr(Arr(df, case_col), B, seed, keys)


def load_members(goals) -> pl.DataFrame:
    ps = [OUT / "R2" / f"members_G{g:02d}.parquet" for g in goals]
    return pl.concat([pl.read_parquet(p) for p in ps if p.exists()], how="vertical_relaxed")


# ============================================================================================ synthetic
def synth_labels(df: pl.DataFrame, world: str, f: float, rng) -> np.ndarray:
    """Redraw which member of each stratum is the adopter (real flags and windows kept)."""
    lab = np.zeros(df.height, bool)
    st = df["sid"].to_numpy()
    order = np.argsort(st, kind="stable")
    s = st[order]
    b = np.flatnonzero(np.r_[True, s[1:] != s[:-1], True])
    w_talk = df["w_talk"].to_numpy().astype(float)[order]
    w_len = df["w_len"].to_numpy().astype(float)[order]
    w_proj = df["w_proj"].to_numpy().astype(float)[order]
    e_eq = df["E_ord_eq"].to_numpy().astype(bool)[order]
    for i0, i1 in zip(b[:-1], b[1:]):
        n = i1 - i0
        if world == "Z1":
            w = w_proj[i0:i1] + 1e-3
        elif world == "Z3":
            w = w_len[i0:i1] + 1.0
        else:
            w = w_talk[i0:i1] + 0.5
        pick = None
        if world == "Z2" and rng.random() < f:
            cand = np.flatnonzero(e_eq[i0:i1])
            if len(cand):
                pick = int(rng.choice(cand))
        if pick is None:
            pick = int(rng.choice(n, p=w / w.sum()))
        lab[order[i0 + pick]] = True
    return lab


def run_synth(df: pl.DataFrame, runs: int = 50) -> pl.DataFrame:
    rows = []
    worlds = [("Z0", 0.0), ("Z1", 0.0), ("Z3", 0.0), ("Z2", 0.25), ("Z2", 0.5)]
    for w, f in worlds:
        for r in range(runs):
            rng = np.random.default_rng(10_000 + 97 * r + int(f * 100) + hash(w) % 13)
            lab = synth_labels(df, w, f, rng)
            d = df.with_columns(pl.Series("syn", lab))
            st = lam_stats(d, "syn")
            ci = boot(d, B=B_SYN, seed=r, case_col="syn")
            rows.append(dict(world=w, f=f, run=r, **{k: v for k, v in st.items()}, lam_lo=ci["Lambda_ci"][0],
                             lam_hi=ci["Lambda_ci"][1]))
        sub = [x for x in rows if x["world"] == w and x["f"] == f]
        lo = np.array([x["lam_lo"] for x in sub], float)
        print(w, f, "median Lambda", np.nanmedian([x["Lambda"] for x in sub]), "share lo>1", np.mean(lo > 1), flush=True)
    return pl.DataFrame(rows)


# ============================================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["build", "synth", "real", "loo"])
    ap.add_argument("--only", default="")
    ap.add_argument("--runs", type=int, default=50)
    a = ap.parse_args()
    goals = [int(x) for x in a.only.split(",") if x] or (PERIODS_MAIN + PERIODS_DESC)
    if a.step == "build":
        tabs = load_tables()
        metas = [build_period(g, tabs) for g in goals]
        (OUT / "R2").mkdir(parents=True, exist_ok=True)
        (OUT / "R2" / "build_meta.json").write_text(json.dumps(metas, indent=1))
        return
    df = load_members([g for g in goals if g in PERIODS_MAIN])
    if a.step == "synth":
        res = run_synth(df, a.runs)
        res.write_parquet(OUT / "R2" / "synth.parquet")
        summ = (res.group_by("world", "f").agg(pl.col("Lambda").median().alias("Lambda_med"),
                                               (pl.col("lam_lo") > 1).mean().alias("share_lo_gt1"), pl.len().alias("runs"))
                .sort("world", "f"))
        print(summ)
        (OUT / "R2" / "synth_summary.json").write_text(json.dumps(summ.to_dicts(), indent=1))
        return
    if a.step == "loo":
        loo()
        return
    real(goals)


def loo():
    """POST HOC diagnostic (added after the real run): pooled Lambda with one period left out."""
    df = load_members(PERIODS_MAIN)
    out = {}
    for g in PERIODS_MAIN:
        d = df.filter(pl.col("goal") != g)
        st = lam_stats(d)
        ci = boot(d, B=B_REAL, seed=2)
        out[f"drop_G{g}"] = dict(Lambda=st["Lambda"], Lambda_ci=ci["Lambda_ci"], OR_ord_eq=st["OR_ord_eq"],
                                 OR_post=st["OR_post"])
        print(g, out[f"drop_G{g}"], flush=True)
    (OUT / "R2" / "loo_posthoc.json").write_text(json.dumps(out, indent=1, default=float))


def real(goals):
    out = {}
    df_all = load_members(goals)
    for g in goals + ["pooled"]:
        d = df_all.filter(pl.col("goal").is_in(PERIODS_MAIN)) if g == "pooled" else df_all.filter(pl.col("goal") == g)
        if d.height == 0:
            continue
        st = lam_stats(d)
        ci = boot(d, B=B_REAL, seed=1, keys=("Lambda", "OR_ord", "OR_ord_eq", "OR_post", "spec"))
        ad = d.filter(pl.col("adopter"))
        desc = dict(n_strata=int(ad.height), n_controls=int(d.height - ad.height),
                    n_strata_with_controls=int(d.group_by("sid").len().filter(pl.col("len") > 1).height),
                    share_ord=float(ad["E_ord"].mean()), share_ord_minus=float(ad["E_ord_minus"].mean()),
                    share_ord_ctrl=float(d.filter(~pl.col("adopter"))["E_ord"].mean()) if d.height > ad.height else None,
                    share_post=float(ad["E_post"].mean()), share_writes_empty=float(ad["writes_empty"].mean()),
                    ch_pull=float(ad["ch_pull"].mean()), ch_page=float(ad["ch_page"].mean()),
                    ch_file=float(ad["ch_file"].mean()), ch_api=float(ad["ch_api"].mean()))
        out[str(g)] = {**st, **ci, **desc}
    # card-literal: violations vs in-cone controls matched on period x delay bin x class (MH risk ratio)
    ic = pl.concat([pl.read_parquet(p) for p in sorted((OUT / "R2").glob("incone_G*.parquet"))], how="vertical_relaxed")
    vi = df_all.filter(pl.col("adopter")).select("goal", "cls", "delay", "E_ord", "clus")
    out["L_ctrl"] = l_ctrl(vi.filter(pl.col("goal").is_in(PERIODS_MAIN)), ic.filter(pl.col("goal").is_in(PERIODS_MAIN)))
    for g in PERIODS_MAIN:
        out["L_ctrl"][f"G{g}"] = l_ctrl(vi.filter(pl.col("goal") == g), ic.filter(pl.col("goal") == g), boot_ci=False)
    (OUT / "R2" / "results_real.json").write_text(json.dumps(out, indent=1, default=float))
    for k, v in out.items():
        print(k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items()} if isinstance(v, dict) else v)


def _dbin(x):
    return np.searchsorted(DBIN_EDGES, x, side="right")


def l_ctrl(vi: pl.DataFrame, ic: pl.DataFrame, boot_ci: bool = True) -> dict:
    vi = vi.with_columns(pl.Series("db", _dbin(vi["delay"].to_numpy())), pl.lit(True).alias("v"))
    ic = ic.with_columns(pl.Series("db", _dbin(ic["delay"].to_numpy())), pl.lit(False).alias("v"))

    def rr(v, c):
        num = den = 0.0
        cs = c.group_by("goal", "db", "cls").agg(pl.col("E_ord").sum().alias("x0"), pl.len().alias("n0"))
        vs = v.group_by("goal", "db", "cls").agg(pl.col("E_ord").sum().alias("x1"), pl.len().alias("n1"))
        j = vs.join(cs, on=["goal", "db", "cls"], how="inner")
        for x1, n1, x0, n0 in zip(j["x1"], j["n1"], j["x0"], j["n0"]):
            N = n1 + n0
            num += x1 * n0 / N
            den += x0 * n1 / N
        return (num / den if den > 0 else np.nan), int(j["n1"].sum()) if j.height else 0

    pt, n_matched = rr(vi, ic)
    res = dict(L_ctrl=pt, n_viol_matched=n_matched, share_viol=float(vi["E_ord"].mean()) if vi.height else None,
               share_incone=float(ic["E_ord"].mean()) if ic.height else None)
    if boot_ci and vi.height:
        rng = np.random.default_rng(3)
        cl = vi["clus"].to_numpy()
        u = np.unique(cl)
        vals = []
        for _ in range(B_REAL):
            pick = rng.choice(u, len(u), replace=True)
            vv = pl.concat([vi.filter(pl.col("clus") == c) for c in pick])
            ii = rng.integers(0, ic.height, ic.height)
            vals.append(rr(vv, ic[ii])[0])
        v = np.array(vals, float)
        v = v[np.isfinite(v)]
        res["L_ctrl_ci"] = (float(np.quantile(v, .025)), float(np.quantile(v, .975))) if len(v) >= 20 else (np.nan, np.nan)
    return res


if __name__ == "__main__":
    main()
