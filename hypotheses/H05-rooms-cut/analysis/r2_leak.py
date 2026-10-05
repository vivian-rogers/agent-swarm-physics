"""H05 round 2, R3: leak conductance of history search and artifacts across rooms (2026-10-05).

Items: novel repositories (artifacts.kind == repo, first agent mention >= 2026-03-16 on a non-reserved day while two
or more rooms exist: goals 35-44 except 40 and the reserved 43; #51 #focus 08-05 -> 08-21). Home room = the first
mentioner's room at birth (rooms_asof.room_at_us). Candidates: agents present on the birth day in another room
(leak population) or in the home room (chat reference). Adoption = first deliberate use (artifact_mentions, how in
{url, bare}, any source). Exposures: search answers naming the repo (search_events.ans_rids, not in q_rids), command
output naming it (how == output, >= 2 s before a deliberate row), chat receipts (ledger items whose message mentions
it). See the card, "Round 2", R3.
"""
from __future__ import annotations

import numpy as np
import polars as pl

from r2_common import FOCUS_DUR, SH, TWO_ROOM_GOALS, assert_no_reserved, reserved_days

W_S = 2 * 3600          # response window (s)
US = 1_000_000


def _us(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy()


def build_inputs(ad: pl.DataFrame) -> dict:
    import rooms_asof as RA  # infra/shared
    res = reserved_days()
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "win_start", "win_end", "goal_no")
    days = sorted(ad["pt_date"].unique().to_list())
    gday = dict(ad.group_by("pt_date").agg(pl.col("goal_no").first()).iter_rows())
    # multi-room windows: segment id and its end (us)
    seg = {}
    for d in days:
        g = gday[d]
        if g in TWO_ROOM_GOALS:
            seg[d] = f"G{g}"
        elif FOCUS_DUR[0] <= d <= FOCUS_DUR[1]:
            seg[d] = "51focus"
    wend = {d: int(e.timestamp() * US) for d, e in zip(cal["pt_date"].to_list(), cal["win_end"].to_list())}
    seg_end = {}
    for d, s in seg.items():
        seg_end[s] = max(seg_end.get(s, 0), wend[d])
    art = pl.read_parquet(SH / "artifacts.parquet").filter(pl.col("kind") == "repo")
    am = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "speaker_kind", "source", "how",
                                                                      "message_id"])
    am = am.filter(pl.col("artifact").is_in(art["artifact"].implode()))
    am = am.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.strftime("%Y-%m-%d").alias("pt_date"))
    am = am.filter(~pl.col("pt_date").is_in(list(res)))
    # birth = first agent mention (any source) of an item whose first mention overall is >= 03-16
    first_all = am.group_by("artifact").agg(pl.col("t").min().alias("t_first_all"))
    ag = am.filter(pl.col("speaker_kind").cast(pl.Utf8) == "agent")
    birth = (ag.sort("t").group_by("artifact").agg(pl.col("t").first().alias("t_birth"), pl.col("agent").first().alias("src"),
                                                   pl.col("pt_date").first().alias("d_birth"))
             .join(first_all, on="artifact").filter(pl.col("t_birth") <= pl.col("t_first_all"))
             .filter(pl.col("d_birth") >= "2026-03-16").filter(pl.col("d_birth").is_in(list(seg))))
    # the overall first mention may sit on a reserved day: reject items whose raw first_t is earlier than t_birth
    birth = birth.join(art.select("artifact", "first_t"), on="artifact").filter(pl.col("first_t") >= pl.col("t_birth") - pl.duration(seconds=1))
    tb = _us(birth["t_birth"])
    home = np.array([RA.room_at_us(int(s), np.array([t]))[0] for s, t in zip(birth["src"].to_list(), tb)])
    birth = birth.with_columns(pl.Series("home", home), pl.Series("tb", tb),
                               pl.col("d_birth").replace_strict(seg, return_dtype=pl.Utf8).alias("seg"))
    birth = birth.filter(pl.col("home") >= 0)
    birth = birth.with_columns(pl.col("seg").replace_strict(seg_end, return_dtype=pl.Int64).alias("t_end"))
    assert_no_reserved(birth["d_birth"].unique().to_list())
    # candidates: agents present on the birth day (panel), not the source
    pres = {d: g["agent"].to_list() for (d,), g in ad.group_by("pt_date")}
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").with_columns(pl.col("t_end").fill_null(pl.datetime(2100, 1, 1, time_zone="UTC")))
    stays = {}
    for a, r, s, e in rt.select("agent", "room", "t_start", "t_end").iter_rows():
        stays.setdefault(int(a), []).append((int(r), int(s.timestamp() * US), int(e.timestamp() * US)))
    rows = []
    for art_id, src, d, t0, h, tend, sg in birth.select("artifact", "src", "d_birth", "tb", "home", "t_end", "seg").iter_rows():
        for b in pres.get(d, []):
            if b == src:
                continue
            rb = int(RA.room_at_us(int(b), np.array([t0]))[0])
            if rb < 0:
                continue
            cross = rb != h
            # censor: first moment b is in the home room after birth (cross) / leaves it (within)
            tc = tend
            for (r, s, e) in stays.get(int(b), []):
                if e <= t0:
                    continue
                if cross and r == h:
                    tc = min(tc, max(s, t0))
                if (not cross) and r != h and s > t0:
                    tc = min(tc, s)
            rows.append((int(art_id), int(b), int(src), d, sg, int(t0), int(h), int(rb), bool(cross), int(tc)))
    cand = pl.DataFrame(rows, orient="row", schema={"artifact": pl.Int32, "b": pl.Int16, "src": pl.Int16, "d_birth": pl.Utf8,
                                                    "seg": pl.Utf8, "tb": pl.Int64, "home": pl.Int16, "room_b": pl.Int16,
                                                    "cross": pl.Boolean, "tc": pl.Int64})
    # adoption: first deliberate use by b after birth
    delib = (ag.filter(pl.col("how").cast(pl.Utf8).is_in(["url", "bare"])).select("artifact", pl.col("agent").cast(pl.Int16).alias("b"), "t")
             .with_columns(pl.col("t").dt.epoch("us").alias("tu")))
    first_delib = cand.select("artifact", "b", "tb").join(delib, on=["artifact", "b"]).filter(pl.col("tu") > pl.col("tb")).group_by(
        "artifact", "b").agg(pl.col("tu").min().alias("t_adopt"))
    cand = cand.join(first_delib, on=["artifact", "b"], how="left")
    # exposures
    outp = (ag.filter((pl.col("source").cast(pl.Utf8) == "action") & (pl.col("how").cast(pl.Utf8) == "output"))
            .select("artifact", pl.col("agent").cast(pl.Int16).alias("b"), pl.col("t").dt.epoch("us").alias("te")))
    wr = pl.read_parquet(SH / "work_repos.parquet", columns=["repo", "artifacts"]).sort("repo").with_row_index("rid")
    rid2art = wr.select(pl.col("rid").cast(pl.Int32), "artifacts").explode("artifacts").rename({"artifacts": "artifact"}).drop_nulls()
    se = pl.read_parquet(SH / "search_events.parquet").filter(~pl.col("holdout") & ~pl.col("pt_date").is_in(list(res)))
    se = se.with_columns(pl.col("t").dt.epoch("us").alias("te"), pl.col("agent").cast(pl.Int16).alias("b"))
    sq = se.select("b", "te", "q_rids").explode("q_rids").rename({"q_rids": "rid"}).drop_nulls()
    sa = se.select("b", "te", "ans_rids").explode("ans_rids").rename({"ans_rids": "rid"}).drop_nulls()
    sa = sa.join(sq, on=["b", "te", "rid"], how="anti").join(rid2art, on="rid").select("artifact", "b", "te")
    sq_art = sq.join(rid2art, on="rid").select("artifact", "b", pl.col("te").alias("tq"))
    # chat receipts: messages mentioning the item -> ledger receipts
    cm = am.filter((pl.col("source").cast(pl.Utf8) == "chat") & pl.col("message_id").is_not_null()).select("artifact", "message_id").unique()
    items_l = (pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id")
               .filter(pl.col("message_id").is_in(cm["message_id"].unique().implode())).collect())
    turns = (pl.scan_parquet(SH / "call_windows.parquet").select("turn_id", "agent", "t_call")
             .filter(pl.col("turn_id").is_in(items_l["turn_id"].unique().implode())).collect())
    chat = (items_l.join(turns, on="turn_id").join(cm, on="message_id")
            .select("artifact", pl.col("agent").cast(pl.Int16).alias("b"), pl.col("t_call").dt.epoch("us").alias("te")))
    return {"cand": cand, "exp": {"search": sa, "output": outp, "chat": chat}, "search_query": sq_art, "delib": delib}


def first_exposures(cand: pl.DataFrame, exp: dict, delib: pl.DataFrame | None = None) -> pl.DataFrame:
    """Per candidate (b, a): first exposure time per channel inside (birth, min(adoption, censor)); output exposures
    must precede the adoption by >= 2 s. Adds t_any (first of search/output/chat)."""
    c = cand
    for ch, e in exp.items():
        j = c.select("artifact", "b", "tb", "tc", "t_adopt").join(e, on=["artifact", "b"])
        lim = pl.min_horizontal(pl.col("tc"), pl.col("t_adopt").fill_null(2 ** 62) - (2 * 1_000_000 if ch == "output" else 0))
        j = j.filter((pl.col("te") > pl.col("tb")) & (pl.col("te") < lim)).group_by("artifact", "b").agg(pl.col("te").min().alias(f"t_{ch}"))
        c = c.join(j, on=["artifact", "b"], how="left")
    return c.with_columns(pl.min_horizontal("t_search", "t_output", "t_chat").alias("t_any"))


def conductance(fe: pl.DataFrame, channel: str, cross: bool, rng, n_placebo: int = 20, n_boot: int = 1000,
                exclude_chat_before: bool = True) -> dict:
    """G = P(adopt within W after the first exposure via `channel`); P0 = the same agent's adoption rate of matched
    placebo items at the same moment. Bootstrap over items."""
    W = W_S * 1_000_000
    pop = fe.filter(pl.col("cross") == cross)
    ev = pop.filter(pl.col(f"t_{channel}").is_not_null())
    if channel != "chat" and exclude_chat_before:
        # a leak exposure counts only if no chat receipt came first (otherwise the item was relayed)
        ev = ev.filter(pl.col("t_chat").is_null() | (pl.col("t_chat") > pl.col(f"t_{channel}")))
    if ev.height == 0:
        return {"n_exposures": 0}
    # placebo pool per agent
    pool = {}
    P = pop.select("b", "artifact", "tb", "tc", "t_adopt", "t_any").to_numpy()
    for b in np.unique(P[:, 0]):
        pool[int(b)] = P[P[:, 0] == b]
    out_items, g_list, p0_list = [], [], []
    E = ev.select("b", "artifact", "tb", "tc", "t_adopt", f"t_{channel}").to_numpy()
    for b, a, tb, tc, ta, te in E:
        b, te = int(b), int(te)
        adopt = 1.0 if (ta is not None and not np.isnan(ta) and te < ta <= te + W and ta <= tc) else 0.0
        if te + W > tc:
            continue  # follow-up shorter than W: drop (adopters too, else the estimate is biased upward)
        Q = pool[b]
        age = te - tb
        qa = Q[:, 4].astype(float)
        qany = Q[:, 5].astype(float)
        ok = ((Q[:, 1] != a) & (Q[:, 2] < te) & (te - Q[:, 2] >= age / 2) & (te - Q[:, 2] <= 2 * age + 1)
              & (Q[:, 3] >= te + W) & (np.isnan(qa) | (qa > te)) & (np.isnan(qany) | (qany > te + W)))
        idx = np.where(ok)[0]
        if len(idx) == 0:
            continue
        if len(idx) > n_placebo:
            idx = rng.choice(idx, n_placebo, replace=False)
        pa = qa[idx]
        p0 = float(np.mean(~np.isnan(pa) & (pa > te) & (pa <= te + W)))
        out_items.append(int(a)); g_list.append(adopt); p0_list.append(p0)
    if not g_list:
        return {"n_exposures": 0}
    it = np.array(out_items); g = np.array(g_list); p0 = np.array(p0_list)
    G, P0 = g.mean(), p0.mean()
    ui = np.unique(it)
    pos = {u: np.where(it == u)[0] for u in ui}
    bs = []
    for _ in range(n_boot):
        pick = rng.choice(ui, len(ui))
        k = np.concatenate([pos[u] for u in pick])
        bs.append((g[k].mean(), p0[k].mean()))
    bs = np.array(bs)
    exc = bs[:, 0] - bs[:, 1]
    with np.errstate(divide="ignore", invalid="ignore"):
        lift = np.where(bs[:, 1] > 0, bs[:, 0] / bs[:, 1], np.nan)
    return {"n_exposures": int(len(g)), "n_items": int(len(ui)), "G": float(G), "P0": float(P0), "excess": float(G - P0),
            "excess_ci95": [float(np.percentile(exc, 2.5)), float(np.percentile(exc, 97.5))],
            "lift": float(G / P0) if P0 > 0 else None,
            "lift_ci95": [float(np.nanpercentile(lift, 2.5)), float(np.nanpercentile(lift, 97.5))] if np.isfinite(lift).any() else None,
            "p_excess_le0": float(np.mean(exc <= 0))}


def routes(fe: pl.DataFrame) -> dict:
    """R3-P3: route of each cross-room adoption."""
    W = W_S * 1_000_000
    t = fe.filter(pl.col("cross") & pl.col("t_adopt").is_not_null() & (pl.col("t_adopt") <= pl.col("tc")))
    n = t.height
    if n == 0:
        return {"n_adoptions": 0}
    chat = t["t_chat"].is_not_null().to_numpy()
    ta = t["t_adopt"].to_numpy()
    s = t["t_search"].to_numpy(); o = t["t_output"].to_numpy()
    s_w = np.array([x is not None and not np.isnan(x) and ta[k] - x <= W for k, x in enumerate(s.astype(float))])
    o_w = np.array([x is not None and not np.isnan(x) and ta[k] - x <= W for k, x in enumerate(o.astype(float))])
    s_any = ~np.isnan(s.astype(float)); o_any = ~np.isnan(o.astype(float))
    leakW = (s_w | o_w) & ~chat
    return {"n_adoptions": int(n), "chat_relay": int(chat.sum()), "search_or_output_within_W_no_chat": int(leakW.sum()),
            "search_within_W_no_chat": int((s_w & ~chat).sum()), "output_within_W_no_chat": int((o_w & ~chat).sum()),
            "search_or_output_earlier_no_chat": int(((s_any | o_any) & ~(s_w | o_w) & ~chat).sum()),
            "no_logged_exposure": int((~chat & ~s_any & ~o_any).sum()),
            "share_leak_within_W": float(leakW.mean())}
