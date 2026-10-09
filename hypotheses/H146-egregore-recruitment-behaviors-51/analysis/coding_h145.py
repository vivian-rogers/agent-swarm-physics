"""H145 element map -> H146 Coding (frozen H145 tables; nothing is re-clustered here).

Inputs (data/processed/H145-ideology-egregores-51/): elements.parquet (eid, kind, key), stmt_cluster.parquet
(srow -> k-means cluster, the frozen seed), expr/w120.parquet + expr/bins_w120.parquet + expr/agents.json (H145's
agent x 2-h-bin expression panel, DQ8 presence-trimmed).

  M_ab   H145's own expression panel (hosts are defined exactly as in H145): agent-bin rows keyed by the epoch 2-h bin
         (H145's 120-min bins start at 16:00 UTC, so they coincide with t // 2 h).
  M_st   statements x E: the statement's cluster element (chat and intents); chat statements also carry the markers
         of their message.
  M_msg  chat items x E: the cluster element of the item's statement, the H34 N/W markers in the item
         (`idea_markers.uses_for_rows`, hashes only), and the repo/project elements the item names
         (`project_mentions_chat`, slug by `memeplex.slug`).
Text is read in memory by idea_markers only; nothing textual is stored.
"""
from __future__ import annotations

import json

import numpy as np
import polars as pl
import scipy.sparse as sp

import h146lib as L

H145 = L.ROOT / "data" / "processed" / "H145-ideology-egregores-51"


def build(ev, _finish_unused=None, h145_dir=H145):
    import idea_markers as IM
    import memeplex as MP
    el = pl.read_parquet(h145_dir / "elements.parquet").sort("eid")
    E = el.height
    assert (el["eid"].to_numpy() == np.arange(E)).all()
    keys = el["key"].to_list()
    kinds = el["kind"].to_list()
    kix = {k: i for i, k in enumerate(keys)}
    a = ev.a
    n_m = a["n_msgs"]
    # ---- statements: clusters
    sc = pl.read_parquet(h145_dir / "stmt_cluster.parquet")
    st = ev.stmts.with_row_index("st_i").join(sc, on="srow", how="left")
    cl_e = np.array([kix.get(f"c:{c}", -1) if c is not None else -1 for c in st["cluster"].to_list()], np.int64)
    ok = cl_e >= 0
    st_i = st["st_i"].to_numpy()
    rows_st = [st_i[ok]]
    cols_st = [cl_e[ok]]
    # chat statement -> msg
    st_msg = st["msg"].to_numpy()
    chat_ok = ok & ~st["msg"].is_null().to_numpy()
    rows_m = [st_msg[chat_ok].astype(np.int64)]
    cols_m = [cl_e[chat_ok]]
    # ---- markers in agent chat items
    cc = pl.read_parquet(L.SH / "chat_core.parquet", columns=["message_id"]).with_row_index("cc")
    mm = ev.msgs.filter(pl.col("skind") == 0).select("message_id", "msg").join(cc, on="message_id", how="inner")
    uses = IM.uses_for_rows(mm["cc"].to_numpy())
    cls_ids = [IM.CLS[c] for c in ("N", "W")]
    uses = uses.filter(pl.col("cls").is_in(cls_ids)).join(
        mm.select(pl.col("cc").cast(pl.UInt32).alias("msg_cc"), pl.col("msg").alias("my_msg")),
        left_on="msg", right_on="msg_cc", how="inner")
    me = np.array([kix.get(f"m:{m}", -1) for m in uses["marker"].to_list()], np.int64)
    okm = me >= 0
    um = uses["my_msg"].to_numpy().astype(np.int64)[okm]
    rows_m.append(um)
    cols_m.append(me[okm])
    # chat statements carry their message's markers
    msg2st = np.full(n_m, -1, np.int64)
    cm = ~st["msg"].is_null().to_numpy()
    msg2st[st_msg[cm].astype(np.int64)] = st_i[cm]
    s_of = msg2st[um]
    rows_st.append(s_of[s_of >= 0])
    cols_st.append(me[okm][s_of >= 0])
    # ---- repo / project names in chat items
    pm = pl.read_parquet(L.SH / "project_mentions_chat.parquet", columns=["message_id", "project"]).join(
        ev.msgs.select("message_id", "msg"), on="message_id", how="inner")
    pi, pj = [], []
    for m, pr in pm.select("msg", "project").iter_rows():
        s = MP.slug(pr)
        for pre in ("r:", "p:"):
            j = kix.get(f"{pre}{s}")
            if j is not None:
                pi.append(m)
                pj.append(j)
    rows_m.append(np.array(pi, np.int64))
    cols_m.append(np.array(pj, np.int64))
    ri = np.concatenate(rows_m)
    rj = np.concatenate(cols_m)
    M_msg = sp.csr_matrix((np.ones(len(ri), np.float32), (ri, rj)), shape=(n_m, E))
    M_msg.data[:] = 1.0
    si = np.concatenate(rows_st)
    sj = np.concatenate(cols_st)
    M_st = sp.csr_matrix((np.ones(len(si), np.float32), (si, sj)), shape=(st.height, E))
    M_st.data[:] = 1.0
    # ---- agent-bin expression: H145's panel
    ex = pl.read_parquet(h145_dir / "expr" / "w120.parquet")
    bins = pl.read_parquet(h145_dir / "expr" / "bins_w120.parquet").sort("bin")
    meta = json.loads((h145_dir / "expr" / "agents.json").read_text())
    agents = np.array(meta["agents"], np.int64)
    t0 = bins["t0"].dt.epoch("us").to_numpy()
    assert (t0 % L.BIN_US == 0).all(), "H145 bins do not coincide with epoch 2-h bins"
    bin_epoch = t0 // L.BIN_US
    dix = {d: i for i, d in enumerate(a["days"])}
    h_days = meta["days"]
    bin_day = np.array([dix.get(h_days[d], -1) for d in bins["day"].to_list()], np.int64)
    ag = agents[ex["agent_row"].to_numpy().astype(np.int64)]
    eb = bin_epoch[ex["bin"].to_numpy().astype(np.int64)]
    key = ag * 10**9 + eb
    uk, inv = np.unique(key, return_inverse=True)
    M_ab = sp.csr_matrix((np.ones(len(inv), np.float32), (inv, ex["eid"].to_numpy().astype(np.int64))),
                         shape=(len(uk), E))
    M_ab.data[:] = 1.0
    ab_day = np.zeros(len(uk), np.int32)
    ab_day[inv] = bin_day[ex["bin"].to_numpy().astype(np.int64)]
    # ---- talk rows: their own chat items
    R = ev.rows
    rr, rm = [], []
    for r, ms in enumerate(R["msgs"].to_list()):
        for m in ms:
            rr.append(r)
            rm.append(m)
    P = sp.csr_matrix((np.ones(len(rr), np.float32), (rr, rm)), shape=(R.height, n_m))
    M_row = (P @ M_msg).tocsr()
    M_row.data[:] = 1.0
    # practice slugs (for the P4 'touched' flag): project/repo elements under both slug forms
    ps = {}
    for i, (k, kd) in enumerate(zip(keys, kinds)):
        if kd in ("repo", "project"):
            ps[i] = k[2:].rstrip("/").split("/")[-1].lower()
    names = keys
    cod = L.Coding(names, kinds, M_msg.tocsr(), M_row, M_ab, (uk // 10**9).astype(np.int16),
                   (uk % 10**9).astype(np.int64), ab_day, "H145 elements (frozen)", ps, M_st.tocsr())
    return cod


def present_keys(h145_dir=H145):
    """H145's DQ8-present agent-bins as epoch keys agent * 1e9 + bin (for restricting other codings)."""
    pr = pl.read_parquet(h145_dir / "expr" / "presence_w120.parquet")
    bins = pl.read_parquet(h145_dir / "expr" / "bins_w120.parquet").sort("bin")
    agents = np.array(json.loads((h145_dir / "expr" / "agents.json").read_text())["agents"], np.int64)
    eb = bins["t0"].dt.epoch("us").to_numpy() // L.BIN_US
    return np.unique(agents[pr["agent_row"].to_numpy().astype(np.int64)] * 10**9
                     + eb[pr["bin"].to_numpy().astype(np.int64)])
