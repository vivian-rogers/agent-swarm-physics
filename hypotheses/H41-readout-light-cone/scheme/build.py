"""H41 scheme: novel items, adoptions, the logged light cone, static hops, hazards and violation channels.

  uv run python hypotheses/H41-readout-light-cone/scheme/build.py markers          # hashed marker uses (H34 rule)
  uv run python hypotheses/H41-readout-light-cone/scheme/build.py periods [--only 38,51] [--workers 2]
  uv run python hypotheses/H41-readout-light-cone/scheme/build.py private          # private-stream channel (text in memory)

Outputs in data/processed/H41-readout-light-cone/ (no text, hashes and ids only):
  markers/uses.parquet         message_id, marker (int64 hash), cls (0 U, 1 D, 2 N, 3 W)   non-holdout chat only
  markers/first_seen.parquet   marker, cls, first_t, first_goal
  G<NN>/items.parquet          one row per novel item: source, t0, room0, adopters
  G<NN>/adoptions.parquet      one row per adoption: cycles, hops, cone status, exposure, covariates, null probabilities
  G<NN>/hazard.parquet         cone-boundary hazard counts per (day, group, cross-room flag)
  G<NN>/violations.parquet     channel flags for adoptions outside the cone (and in-cone unexposed ones)
Read-only imports: hypotheses/H34-idea-cascades/scheme/{markers.py, build_markers.py}.
Holdout days are removed before any text is read or statistic computed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from multiprocessing import get_context
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
H34S = ROOT / "hypotheses/H34-idea-cascades/scheme"
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE))
sys.path.insert(1, str(H34S))
from common import REVISION, git_commit, holdout_mask  # noqa: E402
import h41core as C  # noqa: E402

SH = C.SH
OUT = C.OUT
H_CONE_MIN = 7200.0      # cone horizon at least 2 h
H_HAZ = 7200.0           # hazard horizon 2 h
JIT = 1800.0             # time-shuffle half-width (active seconds)
EARLY = 900.0            # early adoption: within 15 min of t0
W_STATIC = (4 * 3600.0, 24 * 3600.0)


# ============================================================================================ markers
def build_markers():
    import build_markers as BM  # H34, read-only
    import markers as M  # H34, read-only
    t0 = time.time()
    (OUT / "markers").mkdir(parents=True, exist_ok=True)
    chat = BM.non_holdout_chat()
    ids = chat.select("message_id", "msg")
    txt = (pl.scan_parquet(SH / "chat_text.parquet").select("message_id", "text")
           .join(ids.lazy(), on="message_id", how="inner").select("msg", "text").collect().sort("msg"))
    ros = M.roster_full_names(pl.read_parquet(SH / "roster.parquet")["name"].to_list())
    rows, texts = txt["msg"].to_list(), txt["text"].to_list()
    del txt
    step = 4000
    chunks = [(rows[i:i + step], texts[i:i + step]) for i in range(0, len(rows), step)]
    with get_context("spawn").Pool(2, initializer=BM._init, initargs=(ros,)) as pool:
        parts = pool.map(BM._work, chunks, chunksize=1)
    del texts, chunks
    dnw = pl.DataFrame({"msg": np.concatenate([p[0] for p in parts]), "marker": np.concatenate([p[1] for p in parts]),
                        "cls": np.concatenate([p[2] for p in parts])})
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind"])
    am = (pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "source", "how", "message_id"])
          .filter((pl.col("source") == "chat") & pl.col("how").cast(pl.Utf8).is_in(["url", "bare"]))
          .join(art, on="artifact").filter(pl.col("kind").cast(pl.Utf8).is_in(["repo", "site", "file"]))
          .join(ids, on="message_id", how="inner"))
    u = am.select("msg", pl.col("artifact").map_elements(lambda a: M.marker_id("U", str(a)), return_dtype=pl.Int64)
                  .alias("marker"), pl.lit(0, pl.UInt8).alias("cls"))
    uses = pl.concat([u.with_columns(pl.col("msg").cast(pl.UInt32)), dnw]).unique(["msg", "marker"])
    meta = chat.select("msg", "message_id", "t", "goal_no")
    uses = uses.join(meta, on="msg").sort("t", "msg", "marker")
    uses.select("message_id", "marker", "cls").write_parquet(OUT / "markers/uses.parquet", compression="zstd")
    fs = (uses.group_by("marker").agg(pl.col("cls").first(), pl.col("t").min().alias("first_t"),
                                      pl.col("goal_no").sort_by("t").first().alias("first_goal")))
    fs.write_parquet(OUT / "markers/first_seen.parquet", compression="zstd")
    # artifact id -> U marker hash (for the artifact channel)
    amap = am.select("artifact").unique().with_columns(
        pl.col("artifact").map_elements(lambda a: M.marker_id("U", str(a)), return_dtype=pl.Int64).alias("marker"))
    amap.write_parquet(OUT / "markers/u_artifacts.parquet", compression="zstd")
    prov(("markers", {"built_by": "hypotheses/H41-readout-light-cone/scheme/build.py markers",
                      "inputs_tables": ["shared/chat_core", "shared/chat_text (in memory, non-holdout only)",
                                        "shared/artifact_mentions", "shared/artifacts", "shared/roster", "shared/calendar"],
                      "params": {"marker_rule": "H34 scheme/markers.py (imported read-only)", "dictionary_sha1": M.DICT_SHA1}}))
    print(f"markers: {chat.height} msgs, {uses.height} uses, {fs.height} markers, {time.time() - t0:.0f}s", flush=True)


def prov(entry):
    name, d = entry
    p = OUT / "_provenance.json"
    pr = json.loads(p.read_text()) if p.exists() else {}
    pr[name] = {"built_by": d["built_by"], "git_commit": git_commit(),
                "inputs": [{"source": "ai-village", "revision": REVISION, "tables": d["inputs_tables"]}],
                "params": d.get("params", {}), "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p.write_text(json.dumps(pr, indent=1))


# ============================================================================================ eligibility
def eligible_periods() -> list[int]:
    """H34's novelty rule: non-holdout periods >= 5 with >= 10,000 earlier non-holdout chat messages."""
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["pt_date", "goal_no", "t"])
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "holdout"])
    chat = chat.join(cal, on="pt_date", how="left")
    hm = np.array(holdout_mask(chat["pt_date"].to_list(), chat["goal_no"].to_list())) | chat["holdout"].fill_null(False).to_numpy()
    chat = chat.filter(pl.Series(~hm))
    per = chat.group_by("goal_no").agg(pl.col("t").min().alias("t0"), pl.len().alias("n")).sort("t0")
    per = per.with_columns((pl.col("n").cum_sum() - pl.col("n")).alias("earlier"))
    return [int(g) for g in per.filter((pl.col("earlier") >= 10000) & (pl.col("goal_no") >= 5))["goal_no"].to_list()]


# ============================================================================================ period build
def period_items(sk: C.Skeleton, uses: pl.DataFrame, fs: pl.DataFrame, cc: list[int]):
    """Novel items of the period and all their uses (message rows of sk.msgs)."""
    nov = fs.filter(pl.col("first_goal") == sk.goal).select("marker", "cls")
    u = (uses.join(nov.select("marker"), on="marker", how="inner")
         .join(sk.msgs.select("message_id", "mrow", "t", "room", "kind", "agent", "node", "ci_talk", "pt_date"),
               on="message_id", how="inner"))
    return u.sort("marker", "t", "mrow"), nov


def build_period(goal: int):
    t_start = time.time()
    cal = C.calendar()
    sk = C.load_skeleton(goal, cal)
    cc = C.cc_agents()
    uses = pl.read_parquet(OUT / "markers/uses.parquet")
    fs = pl.read_parquet(OUT / "markers/first_seen.parquet")
    u, nov = period_items(sk, uses, fs, cc)
    od = OUT / f"G{goal:02d}"
    od.mkdir(parents=True, exist_ok=True)
    ri = C.RoomIndex(sk)
    items, adf, hz, n_drop_nocall = analyze(sk, u, nov, cal, ri)
    items.write_parquet(od / "items.parquet", compression="zstd")
    if adf.height:
        adf.write_parquet(od / "adoptions.parquet", compression="zstd")
    if hz.height:
        hz.write_parquet(od / "hazard.parquet", compression="zstd")
    if adf.height:
        viol = classify(sk, adf, u, ri, goal)
        viol.write_parquet(od / "violations.parquet", compression="zstd")
    present = set(int(a) for a in sk.agents)
    meta = dict(goal=goal, regime=str(cal.filter(pl.col("goal_no") == goal)["regime"][0]), days=len(sk.days),
                n_agents=len(present), n_items=items.height, n_items_adopted=int((items["n_adopters"] > 0).sum()),
                n_adoptions=adf.height, n_drop_nocall=n_drop_nocall, n_read_events=len(sk.e_t),
                build_s=round(time.time() - t_start, 1))
    (od / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"G{goal:02d}: {meta}", flush=True)
    return meta


def analyze(sk: C.Skeleton, u: pl.DataFrame, nov: pl.DataFrame, cal: pl.DataFrame, ri: C.RoomIndex):
    """Items, adoptions and hazard counts for one skeleton and a table of item uses (real or synthetic)."""
    cc = C.cc_agents()
    present = set(int(a) for a in sk.agents)
    msgs = sk.msgs
    m_t = msgs["t"].to_numpy()
    m_room = msgs["room"].to_numpy()
    m_node = msgs["node"].to_numpy()
    m_day = msgs["pt_date"].to_numpy()
    m_ci = msgs["ci_talk"].to_numpy()
    m_kind = msgs["kind"].to_numpy()

    # ---- sources and adoptions
    first = u.group_by("marker", maintain_order=True).first()
    items = first.select("marker", pl.col("mrow").alias("m0"), pl.col("t").alias("t0"), pl.col("room").alias("room0"),
                         pl.col("node").alias("src"), pl.col("kind").alias("src_kind"), pl.col("pt_date").alias("day0"))
    items = items.join(nov, on="marker", how="left")
    ad = (u.join(items.select("marker", "t0", "src", "m0"), on="marker")
          .filter((pl.col("kind") == "agent") & (pl.col("t") > pl.col("t0")) & (pl.col("node") != pl.col("src"))
                  & ~pl.col("agent").is_in(cc))
          .group_by("marker", "agent", maintain_order=True).first())
    ad = ad.filter(pl.col("agent").is_in(list(present)))
    n_drop_nocall = int(ad["ci_talk"].null_count())
    ad = ad.filter(pl.col("ci_talk").is_not_null())
    nad = ad.group_by("marker").len().rename({"len": "n_adopters"})
    items = items.join(nad, on="marker", how="left").with_columns(pl.col("n_adopters").fill_null(0))

    # carriers: every use of an item (any speaker), for exposure / parents
    carriers = {}
    for mk, mr in zip(u["marker"].to_list(), u["mrow"].to_list()):
        carriers.setdefault(mk, []).append(mr)

    # ---- static graphs (sources in active-time order)
    src_rows = (items.select("m0", "t0", "src", "room0", "day0").unique("m0").sort("t0"))
    at0 = C.active_time(src_rows["t0"].to_numpy(), src_rows["day0"].to_numpy(), cal)
    src_rows = src_rows.with_columns(pl.Series("at0", at0)).sort("at0", "t0")
    sgs = [C.StaticGraph(sk, W) for W in W_STATIC]
    agents_arr = np.array(sorted(present))
    stat_h = {}
    for m0, t0v, srcv, room0v, a0 in zip(src_rows["m0"].to_list(), src_rows["t0"].to_list(), src_rows["src"].to_list(),
                                          src_rows["room0"].to_list(), src_rows["at0"].to_list()):
        seeds_room = [a for a in agents_arr if a != srcv and ri.at(a, t0v) == room0v]
        hs = []
        for sg in sgs:
            A = sg.at_time(a0 if np.isfinite(a0) else -np.inf)
            seeds = set(seeds_room)
            if 0 <= srcv < 64:
                seeds |= set(int(x) for x in np.flatnonzero(A[srcv]) if x != srcv)
            d = C.bfs_hops(A, np.array(sorted(seeds), dtype=int))
            hs.append(d)
        stat_h[m0] = hs

    # ---- per source message: cones, adoptions, hazard
    ad = ad.join(items.select("marker", "cls", "room0", "day0"), on="marker", how="left")
    ad_by_src = {}
    for row in ad.iter_rows(named=True):
        ad_by_src.setdefault(row["m0"], []).append(row)
    items_by_src = {}
    for mk, m0 in zip(items["marker"].to_list(), items["m0"].to_list()):
        items_by_src.setdefault(m0, []).append(mk)
    cls_of = dict(zip(items["marker"].to_list(), items["cls"].to_list()))
    day_end = dict(zip(cal["pt_date"].to_list(), cal["we"].to_list()))
    talk_ci = {a: np.flatnonzero(sk.c_talk[s]) for a, s in sk.agent_calls.items()}  # per-agent talk call indices
    rows_out, haz = [], {}
    n_nodes = C.HUMAN_BASE + 2000
    at_talk = {a: C.active_time(sk.c_first[s_][talk_ci[a]], sk.c_day[s_][talk_ci[a]], cal) for a, s_ in sk.agent_calls.items()}
    src_meta = items.unique("m0").select("m0", "t0", "src", "room0", "day0")
    for r in src_meta.iter_rows(named=True):
        m0, t0v, srcv, room0v, day0 = r["m0"], r["t0"], int(r["src"]), int(r["room0"]), r["day0"]
        adl = ad_by_src.get(m0, [])
        t_last = max([x["t"] for x in adl], default=t0v)
        t_end = min(max(t0v + H_CONE_MIN, t_last + 3600.0), sk.t_max + 1)
        T, K, Hh = C.cone(sk, srcv, t0v, t_end, lenient=False, n_nodes=n_nodes)
        Tl, Kl, _ = C.cone(sk, srcv, t0v, t_end, lenient=True, n_nodes=n_nodes)
        hs4, hs24 = stat_h[m0]
        # ---------------- hazard (2 h horizon, same day)
        de = day_end.get(day0, t0v + H_HAZ)
        hz_end = min(t0v + H_HAZ, de)
        mks = items_by_src[m0]
        adopt_ci = {}  # (marker, agent) -> ci
        for x in adl:
            adopt_ci[(x["marker"], x["agent"])] = x["ci_talk"]
        for a in agents_arr:
            if a == srcv:
                continue
            s = sk.agent_calls[a]
            ct = sk.c_t[s]
            # present after t0 on the day
            if not np.any((ct > t0v) & (ct <= de)):
                continue
            tci = talk_ci[a]
            tf = sk.c_first[s][tci]
            sel = tci[(tf > t0v) & (tf <= hz_end)]
            if len(sel) == 0:
                continue
            in_room0 = ri.at(a, t0v) == room0v
            grp_pre = "pre_in" if in_room0 else "pre_out"
            tf_sel = sk.c_first[s][sel]
            for pref, KK in (("", K), ("L_", Kl)):
                k = KK[a] if KK[a] >= 0 else 10**12
                pm = sel < k
                pre, pre_tf = sel[pm], tf_sel[pm]
                post, post_tf = sel[~pm][:3], tf_sel[~pm][:3]
                for mk in mks:
                    ca = adopt_ci.get((mk, int(a)))
                    cl = cls_of.get(mk, -1)
                    done = False
                    if len(pre):
                        # each pre-entry call is a separate at-risk unit, binned by delay since t0
                        for c, tfc in zip(pre, pre_tf):
                            hit = int(ca is not None and ca == c)
                            _hz_add(haz, day0, pref + grp_pre, in_room0, 1, hit, cl, _dbin(tfc - t0v))
                            if hit:
                                done = True
                                break
                    if done:
                        continue
                    for o, (c, tfc) in enumerate(zip(post, post_tf), start=1):
                        hit = int(ca is not None and ca == c)
                        _hz_add(haz, day0, f"{pref}o{o}", in_room0, 1, hit, cl, _dbin(tfc - t0v))
                        if hit:
                            break
        # ---------------- adoptions
        for x in adl:
            a, ci_use, t_use, mk = int(x["agent"]), int(x["ci_talk"]), x["t"], x["marker"]
            s = sk.agent_calls[a]
            n = C.n_cycles(sk, a, t0v, ci_use, "t")
            n_hi = C.n_cycles(sk, a, t0v, ci_use, "hi")
            n_lo = C.n_cycles(sk, a, t0v, ci_use, "lo")
            # exposure to item-carrying messages read by the adopter at calls <= ci_use
            first_ci, first_tm, last_ci, last_sender, last_tm = None, None, None, None, None
            for cm in carriers.get(mk, []):
                if m_t[cm] >= t_use:
                    break
                ev = sk.readers_of.get(cm)
                if ev is None:
                    continue
                sel = ev[(sk.e_reader[ev] == a) & (sk.e_ci[ev] <= ci_use)]
                if len(sel) == 0:
                    continue
                cie = int(sk.e_ci[sel].min())
                if first_ci is None or cie < first_ci or (cie == first_ci and m_t[cm] < first_tm):
                    first_ci, first_tm = cie, m_t[cm]
                if last_ci is None or cie >= last_ci:
                    last_ci, last_sender, last_tm = cie, int(m_node[cm]), m_t[cm]
            # covariates before the first exposing message (or t0 if unexposed)
            tref = first_tm if first_tm is not None else t0v
            ct = sk.c_t[s]
            w = ct[(ct >= tref - 3600) & (ct < tref)]
            dd = np.diff(w)
            dd = dd[dd <= 1800]
            tau = float(np.median(dd)) if len(dd) >= 3 else np.nan
            room_a = ri.at(a, tref)
            vol = float(np.sum((m_t >= tref - 3600) & (m_t < tref) & (m_room == room_a)))
            # talk calls between exposure and use
            tci = talk_ci[a]
            n_talk_hop = int(np.sum((tci >= first_ci) & (tci <= ci_use))) if first_ci is not None else None
            n_talk_since_t0 = int(np.sum((sk.c_first[s][tci] > t0v) & (tci <= ci_use)))
            # room cone
            r_t0 = ri.at(a, t0v)
            rooms_a = ri.rooms_in(a, t0v, t_use)
            if room0v in rooms_a:
                h_room = 1
            else:
                h_room = np.inf
                for b in agents_arr:
                    if b == a:
                        continue
                    if room0v in ri.rooms_in(b, t0v, t_use):
                        for (tm_, fr, to) in ri.moves(b, t0v, t_use):
                            if to in rooms_a and fr == room0v:
                                h_room = 2
                                break
                    if h_room == 2:
                        break
            # time-shuffle null: candidate talk calls within +-JIT active seconds of the use call
            day_use = x["pt_date"]
            at_use = C.active_time(np.array([t_use]), np.array([day_use]), cal)[0]
            at_all = at_talk[a]
            cand = tci[np.abs(at_all - at_use) <= JIT]
            if len(cand) == 0:
                cand = np.array([ci_use])
            tf_c = sk.c_first[s][cand]
            kk = K[a] if K[a] >= 0 else 10**12
            acaus_c = (tf_c <= t0v) | (cand < kk)
            n_c = np.array([C.n_cycles(sk, a, t0v, int(c), "t") if sk.c_first[s][c] > t0v else 0 for c in cand])
            h4 = hs4[a] if a < 64 else np.inf
            p_jit = float(acaus_c.mean())
            pv_jit = float((n_c < h4).mean())
            rows_out.append(dict(
                marker=mk, cls=int(x["cls"]), m0=m0, src=srcv, t0=t0v, day0=day0,
                room0=room0v, agent=a, mrow=int(x["mrow"]), message_id=x["message_id"], t_use=t_use, day_use=day_use,
                ci_use=ci_use, room_t0=r_t0, cross=(r_t0 != room0v), n=n, n_lo=n_lo, n_hi=n_hi,
                h4=float(h4), h24=float(hs24[a]) if a < 64 else np.inf, h_room=float(h_room),
                K=int(K[a]), K_len=int(Kl[a]), H_tr=int(Hh[a]), T_entry=float(T[a]),
                in_cone=bool(K[a] >= 0 and ci_use >= K[a]), in_cone_len=bool(Kl[a] >= 0 and ci_use >= Kl[a]),
                exposed=first_ci is not None, first_exp_ci=first_ci, first_exp_tm=first_tm,
                parent=last_sender, parent_tm=last_tm,
                cyc_hop=(ci_use - first_ci + 1) if first_ci is not None else None, talk_hop=n_talk_hop,
                n_talk_t0=n_talk_since_t0, dt_hop=(t_use - first_tm) if first_tm is not None else None,
                delay=t_use - t0v, tau_c=tau, vol=vol, p_jit=p_jit, pv_jit=pv_jit, n_cand=int(len(cand))))
    adf = pl.DataFrame(rows_out, infer_schema_length=None) if rows_out else pl.DataFrame()
    if adf.height:
        adf = add_generation(adf)
    items = items.with_columns(pl.col("src").cast(pl.Int64))
    hz = pl.DataFrame([dict(day=k[0], group=k[1], in_room0=k[2], cls=k[3], dbin=k[4], at_risk=v[0], adopt=v[1])
                       for k, v in haz.items()]) if haz else pl.DataFrame()
    return items, adf, hz, n_drop_nocall


DBINS = np.array([30.0, 60.0, 120.0, 300.0, 900.0])


def _dbin(d):
    return int(np.searchsorted(DBINS, d, side="right"))


def _hz_add(haz, day, grp, inr, nrisk, nad, cl=-1, db=-1):
    k = (day, grp, bool(inr), int(cl), int(db))
    v = haz.get(k, [0, 0])
    v[0] += nrisk
    v[1] += nad
    haz[k] = v


def add_generation(adf: pl.DataFrame) -> pl.DataFrame:
    """Generation on the item's exposure tree: source 0; parent agent adopter g+1; human/automated/CC parents -> 1."""
    gens = []
    for mk, grp in adf.sort("marker", "t_use").group_by("marker", maintain_order=True):
        g = {int(grp["src"][0]): 0}
        out = []
        for a, ex, par in zip(grp["agent"].to_list(), grp["exposed"].to_list(), grp["parent"].to_list()):
            if not ex or par is None:
                out.append(None)
                continue
            gp = g.get(int(par))
            gv = (gp + 1) if gp is not None else 1
            g[int(a)] = gv
            out.append(gv)
        gens.append(grp.select("marker", "agent").with_columns(pl.Series("gen", out, dtype=pl.Int16)))
    return adf.join(pl.concat(gens), on=["marker", "agent"], how="left")


# ============================================================================================ channels
def classify(sk: C.Skeleton, adf: pl.DataFrame, u: pl.DataFrame, ri: C.RoomIndex, goal: int) -> pl.DataFrame:
    """Channel flags for acausal adoptions (outside the logged cone) and in-cone never-exposed adoptions."""
    viol = adf.filter(~pl.col("in_cone") | ~pl.col("exposed")).with_columns(pl.lit(False).alias("control"))
    ctrl_pool = adf.filter(pl.col("in_cone") & pl.col("exposed"))
    ctrl = ctrl_pool.sample(n=min(500, ctrl_pool.height), seed=goal).with_columns(pl.lit(True).alias("control")) \
        if ctrl_pool.height else ctrl_pool.with_columns(pl.lit(True).alias("control"))
    sel = pl.concat([viol, ctrl], how="vertical_relaxed")
    if sel.height == 0:
        return pl.DataFrame()
    msgs = sk.msgs
    # templated flags at message level
    st = pl.read_parquet(SH / "embeddings/statements.parquet", columns=["kind", "src_row"]).with_row_index("srow")
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("src_row").with_columns(
        pl.col("src_row").cast(pl.UInt32))
    sf = pl.read_parquet(SH / "statement_flags.parquet", columns=["srow", "templated_bge", "templated_gte"])
    tmpl = (st.filter(pl.col("kind") == "chat").join(ci, on="src_row").join(sf, on="srow")
            .select("message_id", (pl.col("templated_bge") | pl.col("templated_gte")).alias("templated")))
    tset = set(tmpl.filter(pl.col("templated"))["message_id"].to_list())
    # reply parents
    rp = (pl.scan_parquet(SH / "reply_pairs.parquet").filter((pl.col("goal_no") == goal) & pl.col("parent"))
          .select("B_message_id", "A_message_id").collect())
    parent_of = dict(zip(rp["B_message_id"].to_list(), rp["A_message_id"].to_list()))
    # artifacts
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "kind", "parent"])
    kind_of = dict(zip(art["artifact"].to_list(), art["kind"].cast(pl.Utf8).to_list()))
    par_of = dict(zip(art["artifact"].to_list(), art["parent"].to_list()))
    am = (pl.scan_parquet(SH / "artifact_mentions.parquet")
          .filter((pl.col("t") >= pl.from_epoch(pl.lit(int((sk.t_min - 86400) * 1e6)), time_unit="us").dt.replace_time_zone("UTC"))
                  & (pl.col("t") <= pl.from_epoch(pl.lit(int((sk.t_max + 3600) * 1e6)), time_unit="us").dt.replace_time_zone("UTC")))
          .select("artifact", C.ts("t").alias("t"), "agent", pl.col("source").cast(pl.Utf8).alias("source"),
                  pl.col("how").cast(pl.Utf8).alias("how"), "message_id").collect())
    am_chat = am.filter(pl.col("source") == "chat")
    chat_arts = {}
    for mid, a in zip(am_chat["message_id"].to_list(), am_chat["artifact"].to_list()):
        chat_arts.setdefault(mid, set()).add(a)
    amx = am.filter(pl.col("source").is_in(["action", "intention"]) & pl.col("how").is_in(["url", "output", "bare", "cwd"]))
    by_agent = {}
    for a, t, art_ in zip(amx["agent"].to_list(), amx["t"].to_list(), amx["artifact"].to_list()):
        by_agent.setdefault(a, []).append((t, art_))
    for a in by_agent:
        by_agent[a].sort()
    by_agent_np = {a: (np.array([x[0] for x in v]), np.array([x[1] for x in v])) for a, v in by_agent.items()}
    umap = pl.read_parquet(OUT / "markers/u_artifacts.parquet")
    art_of_marker = dict(zip(umap["marker"].to_list(), umap["artifact"].to_list()))
    m_mid = msgs["message_id"].to_list()
    # non-agent / CC uses per item
    cc = set(C.cc_agents())
    ext = u.filter((pl.col("kind") != "agent") | pl.col("agent").is_in(list(cc)))
    ext_uses = {}
    for mk, mr, t in zip(ext["marker"].to_list(), ext["mrow"].to_list(), ext["t"].to_list()):
        ext_uses.setdefault(mk, []).append((t, mr))

    def touched(agent, t_lo, t_hi):
        v = by_agent_np.get(agent)
        if v is None:
            return set()
        i0, i1 = np.searchsorted(v[0], t_lo), np.searchsorted(v[0], t_hi)
        s = set(v[1][i0:i1].tolist())
        return s | {par_of[x] for x in s if par_of.get(x) is not None}

    out = []
    for x in sel.iter_rows(named=True):
        a, mk, t0, t_use, ci_use = x["agent"], x["marker"], x["t0"], x["t_use"], x["ci_use"]
        f = dict(marker=mk, agent=a, in_cone=x["in_cone"], exposed=x["exposed"], control=x["control"])
        f["timing"] = bool(x["in_cone_len"]) and not x["in_cone"]
        f["templated"] = x["message_id"] in tset
        inj_vis, inj_other = False, False
        for (te, mr) in ext_uses.get(mk, []):
            if te >= t_use:
                break
            ev = sk.readers_of.get(mr)
            seen = ev is not None and np.any((sk.e_reader[ev] == a) & (sk.e_ci[ev] <= ci_use))
            inj_vis |= bool(seen)
            inj_other |= not bool(seen)
        f["human_logged"] = inj_vis
        f["human_crosspost"] = inj_other and not inj_vis
        src_mid = m_mid[x["m0"]]
        pa, pb = parent_of.get(src_mid), parent_of.get(x["message_id"])
        f["common_stimulus"] = pa is not None and pa == pb
        # artifacts
        src_set = set(chat_arts.get(src_mid, set()))
        if 0 <= x["src"] < 64:
            v = by_agent_np.get(x["src"])
            if v is not None:
                i0, i1 = np.searchsorted(v[0], t0 - 7200), np.searchsorted(v[0], t0 + 1e-6)
                src_set |= set(v[1][i0:i1].tolist())
        src_set |= {par_of[y] for y in list(src_set) if par_of.get(y) is not None}
        item_art = art_of_marker.get(mk) if x["cls"] == 0 else None
        tch = touched(a, t0 - 6 * 3600, t_use)
        hit = set()
        if item_art is not None:
            if item_art in tch or par_of.get(item_art) in tch:
                hit.add(item_art)
        hit |= (tch & src_set)
        kinds = {kind_of.get(y) for y in hit}
        f["artifact"] = bool(kinds & {"repo", "file"})
        f["web"] = bool(kinds & {"site", "domain"})
        # search calls and room moves
        s = sk.agent_calls[a]
        ck, ct = sk.c_kind[s], sk.c_t[s]
        f["search"] = bool(np.any((ck == "search") & (ct > t0) & (ct <= t_use)))
        f["room_move"] = len(ri.moves(a, t0, t_use)) > 0
        f["private"] = None  # filled by the `private` step
        out.append(f)
    return pl.DataFrame(out, infer_schema_length=None)


# ============================================================================================ private stream
def reclassify(goal: int):
    """Re-run the channel classification (with an in-cone control sample) from the saved adoptions."""
    cal = C.calendar()
    sk = C.load_skeleton(goal, cal)
    uses = pl.read_parquet(OUT / "markers/uses.parquet")
    fs = pl.read_parquet(OUT / "markers/first_seen.parquet")
    u, _ = period_items(sk, uses, fs, C.cc_agents())
    adf = pl.read_parquet(OUT / f"G{goal:02d}/adoptions.parquet")
    v = classify(sk, adf, u, C.RoomIndex(sk), goal)
    v.write_parquet(OUT / f"G{goal:02d}/violations.parquet", compression="zstd")
    print(f"classify G{goal:02d}: {v.height} rows ({int(v['control'].sum())} controls)", flush=True)


def build_private(goals):
    """Private-stream channel: does the item's marker occur in the adopter's own intentions or commands before use?

    Text is read in memory only (non-holdout days), hashed with H34's rule, and never written.
    """
    import markers as M  # H34, read-only
    M.dictionary()
    ros = M.roster_full_names(pl.read_parquet(SH / "roster.parquet")["name"].to_list())
    cal = C.calendar()
    hold_days = set(cal.filter(pl.col("hold"))["pt_date"].to_list())
    it = pl.read_parquet(SH / "intentions.parquet").join(pl.read_parquet(SH / "intentions_text.parquet"),
                                                          on="event_index", how="left")
    it = it.with_columns(C.ts("t").alias("ts"), pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date()
                         .cast(pl.Utf8).alias("pt"))
    it = it.filter(~pl.col("pt").is_in(list(hold_days)))
    cmd = (pl.scan_parquet(SH / "artifact_commands_text.parquet").select("t", "agent", "cmd")
           .filter(pl.col("cmd").is_not_null()).collect())
    cmd = cmd.with_columns(C.ts("t").alias("ts"), pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date()
                           .cast(pl.Utf8).alias("pt")).filter(~pl.col("pt").is_in(list(hold_days)))
    for g in goals:
        p = OUT / f"G{g:02d}/violations.parquet"
        if not p.exists():
            continue
        v = pl.read_parquet(p)
        if v.height == 0:
            continue
        adf = pl.read_parquet(OUT / f"G{g:02d}/adoptions.parquet", columns=["marker", "agent", "t_use"])
        v2 = v.join(adf, on=["marker", "agent"], how="left")
        res = []
        for a, grp in v2.group_by("agent"):
            a = a[0]
            tmin, tmax = grp["t_use"].min() - 86400, grp["t_use"].max()
            texts = []
            ii = it.filter((pl.col("agent") == a) & (pl.col("ts") >= tmin) & (pl.col("ts") < tmax))
            for tsv, gt, sh in zip(ii["ts"].to_list(), ii["goal_text"].to_list(), ii["short_text"].to_list()):
                texts.append((tsv, (gt or "") + "\n" + (sh or "")))
            cc_ = cmd.filter((pl.col("agent") == a) & (pl.col("ts") >= tmin) & (pl.col("ts") < tmax))
            for tsv, c_ in zip(cc_["ts"].to_list(), cc_["cmd"].to_list()):
                texts.append((tsv, c_))
            texts.sort(key=lambda z: z[0])
            tarr = np.array([z[0] for z in texts]) if texts else np.array([])
            hashes = [set(M.marker_id(c, xx) for c, xx in M.extract(z[1], ros)) for z in texts]
            for mk, tu in zip(grp["marker"].to_list(), grp["t_use"].to_list()):
                i0, i1 = np.searchsorted(tarr, tu - 86400), np.searchsorted(tarr, tu)
                hitp = any(mk in hashes[k] for k in range(i0, i1))
                res.append(dict(marker=mk, agent=a, private=hitp))
        del texts
        r = pl.DataFrame(res) if res else pl.DataFrame({"marker": [], "agent": [], "private": []})
        v = v.drop("private").join(r, on=["marker", "agent"], how="left").with_columns(pl.col("private").fill_null(False))
        v.write_parquet(p, compression="zstd")
        print(f"private G{g:02d}: {v.height} rows, private {int(v['private'].sum())}", flush=True)


# ============================================================================================ main
def _run(g):
    try:
        return build_period(g)
    except Exception as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        return {"goal": g, "error": repr(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["markers", "periods", "private", "eligible", "classify"])
    ap.add_argument("--only", default="")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.step == "markers":
        build_markers()
        return
    goals = [int(x) for x in a.only.split(",") if x] or eligible_periods()
    if a.step == "eligible":
        print(goals)
        return
    if a.step == "classify":
        for g in goals:
            reclassify(g)
        return
    if a.step == "private":
        build_private(goals)
        prov(("private", {"built_by": "hypotheses/H41-readout-light-cone/scheme/build.py private",
                          "inputs_tables": ["shared/intentions", "shared/intentions_text (in memory)",
                                            "shared/artifact_commands_text (in memory)", "shared/calendar"],
                          "params": {"window_s": 86400, "holdout": "days removed before reading text"}}))
        return
    t0 = time.time()
    if a.workers > 1 and len(goals) > 1:
        with get_context("spawn").Pool(min(a.workers, 2)) as pool:
            metas = pool.map(_run, sorted(goals, key=lambda g: -g), chunksize=1)
    else:
        metas = [_run(g) for g in goals]
    (OUT / "periods_meta.json").write_text(json.dumps(metas, indent=1))
    prov(("periods", {"built_by": "hypotheses/H41-readout-light-cone/scheme/build.py periods",
                      "inputs_tables": ["shared/call_windows", "shared/context_ledger_items", "shared/chat_core",
                                        "shared/rooms_timeline", "shared/calendar", "shared/roster",
                                        "shared/artifact_mentions", "shared/artifacts", "shared/statement_flags",
                                        "shared/embeddings/statements", "shared/embeddings/chat_index",
                                        "shared/reply_pairs", "H41 markers/"],
                      "params": {"cone_horizon_min_s": H_CONE_MIN, "hazard_horizon_s": H_HAZ, "jitter_s": JIT,
                                 "static_windows_active_s": list(W_STATIC), "early_s": EARLY, "periods": goals}}))
    print(f"periods done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
