"""H40 round 2 (2026-10-05): R6 negative eta (G38, G44), R1 regime-I span split, R5 collapse with matched coupling.

Pre-registration: card section "Round 2". Reserved data never enter (round-1 items are built with holdout_mask).

  uv run python hypotheses/H40-call-clock-coupling/analysis/round2.py r6 --period 38 [--B 50]
  uv run python hypotheses/H40-call-clock-coupling/analysis/round2.py r6syn --period 38 [--reps 10]
  uv run python hypotheses/H40-call-clock-coupling/analysis/round2.py r1 [--B 50]
  uv run python hypotheses/H40-call-clock-coupling/analysis/round2.py r1syn [--reps 20]
  uv run python hypotheses/H40-call-clock-coupling/analysis/round2.py r5
  uv run python hypotheses/H40-call-clock-coupling/analysis/round2.py r5syn --period 38 [--reps 10]

Outputs: data/processed/H40-call-clock-coupling/round2/*.json (codes and statistics only).
The round-1 pipeline is untouched: round 2 is a separate entry point (STANDARDS section 5, switches).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import polars as pl
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h40lib as L  # noqa: E402

R2 = L.OUT / "round2"
KIND = ['cu_action', 'talk', 'pause', 'wait', 'consolidate', 'session_start', 'session_stop', 'search', 'room_move',
        'request']
R1_PERIODS = [24, 25, 26, 27, 30, 31]
E_STEPS = np.array([8.0, 16.0, 32.0, 64.0])          # D0 step edges (s)


# ============================================================================= extra per-call arrays

@dataclass
class Extra:
    kind: np.ndarray
    t_log: np.ndarray
    t_first: np.ndarray
    logged: np.ndarray
    api: np.ndarray          # dur_api_s (nan where not logged)
    room: np.ndarray
    n_ment: np.ndarray
    n_human: np.ndarray
    n_agent: np.ndarray
    n_rows: np.ndarray       # calls table (regime III), -1 elsewhere
    fail: np.ndarray
    write: np.ndarray
    lab: dict                # agent -> lab


def load_extra(n: int) -> Extra:
    cw = pl.read_parquet(L.SH / "call_windows.parquet", columns=["turn_id", "kind", "t_log", "t_first", "start_src",
                                                                    "dur_api_s"]).sort("turn_id")
    assert cw.height == n
    lt = pl.read_parquet(L.SH / "context_ledger_turns.parquet", columns=["turn_id", "room", "n_ment", "n_human",
                                                                           "n_agent"]).sort("turn_id")
    ca = pl.read_parquet(L.SH / "calls.parquet", columns=["turn_id", "n_rows", "fail", "any_write"])
    nr = np.full(n, -1, np.int32); fl = np.zeros(n, bool); wr = np.zeros(n, bool)
    tid = ca["turn_id"].to_numpy()
    nr[tid] = ca["n_rows"].fill_null(0).to_numpy(); fl[tid] = ca["fail"].fill_null(0).to_numpy() > 0
    wr[tid] = ca["any_write"].fill_null(False).to_numpy()
    kc = cw["kind"].cast(pl.String).replace_strict({k: i for i, k in enumerate(KIND)}, default=0).to_numpy()
    ro = L.roster()
    return Extra(kind=kc.astype(np.int8), t_log=L._sec(cw["t_log"]), t_first=L._sec(cw["t_first"]),
                 logged=(cw["start_src"].cast(pl.String) == "logged").to_numpy(),
                 api=cw["dur_api_s"].fill_null(np.nan).to_numpy().astype(np.float64),
                 room=lt["room"].fill_null(-1).to_numpy().astype(np.int16),
                 n_ment=lt["n_ment"].fill_null(0).to_numpy(), n_human=lt["n_human"].fill_null(0).to_numpy(),
                 n_agent=lt["n_agent"].fill_null(0).to_numpy(), n_rows=nr, fail=fl, write=wr,
                 lab=dict(zip(ro["agent"].to_list(), ro["lab"].fill_null("?").to_list())))


# ============================================================================= items, rows, features

def load_items(goal: int, calls: L.Calls, btid: pl.DataFrame | None = None, with_ids: bool = False) -> pl.DataFrame:
    """Round-1 items; with_ids rebuilds them with message ids (needed for third-party replies) and checks alignment."""
    d = L.OUT / f"G{goal:02d}"
    it = pl.read_parquet(d / "items.parquet").sort("item")
    if not with_ids:
        return it
    units = L.unit_map()
    full = L.build_items(calls, goal, units, btid)
    full = full.select("item", "message_id", "c1", "t_m", "recv")
    j = it.join(full, on="item", how="left", suffix="_b")
    assert (j["c1"] == j["c1_b"]).all() and np.allclose(j["t_m"].to_numpy(), j["t_m_b"].to_numpy()), "item mismatch"
    return j.drop("c1_b", "t_m_b", "recv_b")


def expand_all(calls: L.Calls, it: pl.DataFrame, horizon: float = L.H_FIT_S) -> L.Rows:
    c1 = it["c1"].to_numpy(); t_m = it["t_m"].to_numpy(); rank = it["rank"].to_numpy().astype(np.int64)
    day = it["day"].to_numpy()
    parts = []
    for dd in np.unique(day):
        s = np.flatnonzero(day == dd)
        r = L.expand(calls, c1[s], t_m[s], rank[s], horizon=horizon)
        r.item = s[r.item]
        parts.append(r)
    return L.Rows(**{f: np.concatenate([getattr(p, f) for p in parts]) for f in L.Rows.__dataclass_fields__})


def third_party_counts(goal: int, it: pl.DataFrame, rows: L.Rows, calls: L.Calls, kB: np.ndarray | None = None) -> np.ndarray:
    """Per row: DQ2 parent replies to m by agents other than the recipient and the sender, posted before t_call,n."""
    OFF = 1e6
    if kB is None:
        kB = third_party_keys(goal, it)
    t_m = it["t_m"].to_numpy()
    kr = rows.item.astype(np.float64) * 4 * OFF + OFF + np.clip(calls.t[rows.tid] - t_m[rows.item], -OFF / 2, OFF)
    k0 = rows.item.astype(np.float64) * 4 * OFF
    return (np.searchsorted(kB, kr, side="left") - np.searchsorted(kB, k0, side="left")).astype(np.int32)


def third_party_keys(goal: int, it: pl.DataFrame) -> np.ndarray:
    rp = (pl.scan_parquet(L.SH / "reply_pairs.parquet")
          .filter((pl.col("pair_set").cast(pl.String) == "cand") & pl.col("parent") & (pl.col("goal_no") == goal)
                  & ~pl.col("holdout")).select("A_message_id", "B_message_id", "b_agent").collect())
    ch = pl.read_parquet(L.SH / "chat_core.parquet", columns=["message_id", "t"])
    rp = rp.join(ch.rename({"message_id": "B_message_id", "t": "tB"}), on="B_message_id", how="inner")
    rp = rp.with_columns(pl.Series("tBs", L._sec(rp["tB"])))
    m = it.select("item", "message_id", "recv", "sender", "t_m").join(
        rp.rename({"A_message_id": "message_id"}), on="message_id", how="inner")
    m = m.filter((pl.col("b_agent").cast(pl.Int16) != pl.col("recv").cast(pl.Int16))
                 & (pl.col("b_agent").cast(pl.Int16) != pl.col("sender").cast(pl.Int16)))
    OFF = 1e6
    return np.sort(m["item"].to_numpy().astype(np.float64) * 4 * OFF + OFF + np.clip(m["tBs"].to_numpy() - m["t_m"].to_numpy(), -OFF / 2, OFF))


def features(rows: L.Rows, it: pl.DataFrame, calls: L.Calls, X: Extra, third: np.ndarray | None = None) -> dict:
    """Row-level arrays for every round-2 design."""
    i = rows.item
    tid = rows.tid
    prev = np.maximum(tid - 1, 0)
    first = rows.n == 1
    t_m = it["t_m"].to_numpy()
    hod = np.floor(np.mod(t_m - 8 * 3600, 86400.0) / 3600.0).astype(np.int64)     # hour of day of arrival (UTC-8)
    block_item = it["day"].to_numpy().astype(np.int64) * 100 + hod                 # 1-hour bootstrap blocks
    prow = np.r_[-1, tid[:-1]]
    prow[first] = -1
    f = dict(
        item=i, tid=tid, first=first, n=rows.n, a=rows.a, e=rows.e, b=rows.b, k=rows.k, gap=rows.gap,
        chat=rows.chat, reset=rows.reset, prev_talk=rows.prev_talk,
        au=it["au"].to_numpy()[i], day=it["day"].to_numpy()[i], ment=it["ment"].to_numpy()[i].astype(np.int8),
        rank=it["rank"].to_numpy()[i].astype(np.int64), block=block_item[i],
        room1=X.room[it["c1"].to_numpy()][i], recv=it["recv"].to_numpy()[i],
        talk=calls.talk[tid], prev_kind=X.kind[prev], prev_rows=np.maximum(X.n_rows[prev], 0),
        prev_fail=X.fail[prev], prev_write=X.write[prev], n_ment_n=X.n_ment[tid], n_human_n=X.n_human[tid],
        n_agent_n=X.n_agent[tid], prev_is_row=(prow == tid - 1),
        logged_n=X.logged[tid], logged_p=X.logged[prev], chat_p=calls.chat[prev],
        api_p=X.api[prev], busy_p=X.t_log[prev] - calls.t[prev], wait_n=calls.t[tid] - X.t_log[prev],
    )
    if third is not None:
        f["third"] = third
    return f


# ============================================================================= generic cells and design

BASE_KEYS = ["nb", "ab", "eb", "kb", "bb", "rb", "gap", "chat", "ment", "reset", "pt"]


def row_frame(f: dict, y: np.ndarray, fe: np.ndarray, sel: np.ndarray | None = None, extra_cont: dict | None = None,
              extra_keys: dict | None = None) -> pl.DataFrame:
    """Row frame with binned keys (as h40lib.aggregate) and the log covariates to be summed within cells."""
    s = np.ones(len(y), bool) if sel is None else sel
    first = f["first"][s]
    d = {
        "block": f["block"][s], "fe": fe[s],
        "nb": np.searchsorted(L.N_EDGES, f["n"][s]).astype(np.int8),
        "ab": np.searchsorted(L.A_EDGES, f["a"][s]).astype(np.int8),
        "eb": np.searchsorted(L.E_EDGES, f["e"][s]).astype(np.int8),
        "kb": np.searchsorted(L.K_EDGES, f["k"][s]).astype(np.int8),
        "bb": np.searchsorted(L.B_EDGES, f["b"][s]).astype(np.int8),
        "rb": np.where(first, np.searchsorted(L.R_EDGES, f["rank"][s]), 0).astype(np.int8),
        "gap": f["gap"][s].astype(np.int8), "chat": f["chat"][s].astype(np.int8), "ment": f["ment"][s].astype(np.int8),
        "reset": f["reset"][s].astype(np.int8), "pt": f["prev_talk"][s].astype(np.int8),
        "y": y[s].astype(np.float64),
        "c_logn": np.log(f["n"][s]), "c_loga": np.log(np.maximum(f["a"][s], 1.0) / 60.0),
        "c_loge": np.log(f["e"][s] / 10.0), "c_logk": np.log1p(f["k"][s]), "c_logb": np.log1p(f["b"][s]),
        "c_logr": np.where(first, np.log(f["rank"][s]), 0.0),
    }
    for nm, v in (extra_cont or {}).items():
        d["c_" + nm] = np.asarray(v)[s].astype(np.float64)
    for nm, v in (extra_keys or {}).items():
        d[nm] = np.asarray(v)[s].astype(np.int16)
    return pl.DataFrame(d)


def cells_of(rf: pl.DataFrame) -> pl.DataFrame:
    keys = [c for c in rf.columns if not c.startswith("c_") and c != "y"]
    cont = [c for c in rf.columns if c.startswith("c_")]
    return rf.group_by(keys).agg([pl.len().alias("N"), pl.col("y").sum()] + [pl.col(c).sum() for c in cont])


def design2(cells: pl.DataFrame, eta_mode: str = "base", extra_cont_later: list | None = None,
            extra_cat_later: list | None = None):
    N = cells["N"].to_numpy().astype(float)
    m = {c[2:]: cells[c].to_numpy() / np.maximum(N, 1e-12) for c in cells.columns if c.startswith("c_")}
    first = (cells["nb"].to_numpy() == 0).astype(float)
    later = 1.0 - first
    gap = cells["gap"].to_numpy()
    chat = cells["chat"].to_numpy().astype(float)
    ment = cells["ment"].to_numpy().astype(float)
    cols, names = [], []

    def add(v, nm):
        v = np.asarray(v, dtype=float)
        if np.any(v != 0):
            cols.append(v); names.append(nm)
    add(first, "n1"); add(first * m["logr"], "n1_logrank"); add(first * ment, "n1_ment"); add(later * ment, "ment")
    add(m["logk"], "logk"); add(cells["pt"].to_numpy(), "prev_talk"); add(later * cells["reset"].to_numpy(), "reset_since")
    if chat.any() and not chat.all():
        add(chat, "chat")
    for g in range(1, len(L.GAPS)):
        add(later * (gap == g), f"gap_{L.GAPS[g]}")
        add(first * (gap == g), f"n1_gap_{L.GAPS[g]}")
    add(first * m["loga"], "eta1"); add(later * m["logn"], "phi"); add(later * m["loga"], "psi")
    add(later * m["logb"], "chi")
    if eta_mode == "base":
        add(later * m["loge"], "eta")
    elif eta_mode == "split_busy_wait":
        add(later * m["logbusy"], "eta_busy"); add(later * m["logwait"], "eta_wait")
    elif eta_mode == "split_api":
        add(later * m["logapi"], "eta_api"); add(later * m["logrest"], "eta_rest")
    elif eta_mode == "steps":
        eb = cells["estep"].to_numpy()
        for j in range(1, len(E_STEPS) + 1):
            add(later * (eb == j), f"estep_{j}")
    for nm in extra_cont_later or []:
        add(later * m[nm], nm)
    for nm in extra_cat_later or []:
        v = cells[nm].to_numpy()
        for lv in sorted(set(v.tolist()) - {0}):
            add(later * (v == lv), f"{nm}_{lv}")
    fe = cells["fe"].to_numpy().astype(np.int64)
    FE = sp.csr_matrix((np.ones(len(fe)), (np.arange(len(fe)), fe)), shape=(len(fe), int(fe.max()) + 1))
    return FE, np.column_stack(cols), np.zeros(len(N)), names


def fit_spec(cells, w=None, start=None, maxit=60, **kw):
    FE, Xm, off, names = design2(cells, **kw)
    f, full = L.fit(FE, Xm, off, cells["y"].to_numpy(), cells["N"].to_numpy().astype(float), w=w, start=start, maxit=maxit)
    f.names = names
    return f, full


def boot_weights(cells_list, B, seed):
    """Paired block weights: one multinomial draw over the union of blocks, mapped onto each cell table."""
    blocks = np.unique(np.concatenate([c["block"].to_numpy() for c in cells_list]))
    rng = np.random.default_rng(seed)
    W = rng.multinomial(len(blocks), np.ones(len(blocks)) / len(blocks), size=B).astype(float)
    return blocks, W


def run_specs(specs: dict, B: int, seed: int, coefs=("eta",)) -> dict:
    """specs: name -> (cells, kwargs). Point fits with model SEs, paired block bootstrap, and paired deltas vs 'base'."""
    out = {}
    blocks, W = boot_weights([c for c, _ in specs.values()], B, seed)
    draws = {}
    for nm, (cells, kw) in specs.items():
        f, full = fit_spec(cells, **kw)
        bi = np.searchsorted(blocks, cells["block"].to_numpy())
        dr = []
        for b in range(B):
            fb, _ = fit_spec(cells, w=W[b][bi], start=full, maxit=25, **kw)
            dr.append({k: fb.get(k) for k in fb.names})
        draws[nm] = dr
        res = dict(coef={k: f.get(k) for k in f.names}, model_se={k: f.se(k) for k in f.names},
                   n_rows=float(cells["N"].sum()), n_y=float(cells["y"].sum()), n_cells=cells.height,
                   n_fe=int(cells["fe"].max()) + 1, converged=bool(f.converged))
        res["boot_se"] = {k: float(np.nanstd([d.get(k, np.nan) for d in dr])) for k in f.names}
        res["se"] = {k: float(np.nanmax([res["boot_se"][k], res["model_se"][k]])) for k in f.names}
        res["ci"] = {k: [res["coef"][k] - 1.96 * res["se"][k], res["coef"][k] + 1.96 * res["se"][k]] for k in f.names}
        out[nm] = res
    if "base" in out:
        for nm in out:
            if nm == "base":
                continue
            for c in coefs:
                if c in out[nm]["coef"] and c in out["base"]["coef"]:
                    dd = np.array([draws[nm][b].get(c, np.nan) - draws["base"][b].get(c, np.nan) for b in range(B)])
                    est = out[nm]["coef"][c] - out["base"]["coef"][c]
                    se = float(np.nanstd(dd))
                    out[nm][f"delta_{c}"] = dict(est=est, se=se, lo=est - 1.96 * se, hi=est + 1.96 * se)
    return out


def fe_codes(*cols) -> np.ndarray:
    key = np.zeros(len(cols[0]), dtype=np.int64)
    for c in cols:
        c = np.asarray(c).astype(np.int64)
        key = key * 100003 + (c - c.min())
    _, inv = np.unique(key, return_inverse=True)
    return inv.astype(np.int32)


# ============================================================================= R6 (real data and synthetic)

def r6_specs(f: dict, y: np.ndarray, X: Extra, which=("base", "D0", "D1_talk", "D1_reptalk", "D2", "D3", "D4", "D5", "D6")):
    later = ~f["first"]
    fe_au = f["au"].astype(np.int32)
    specs = {}
    if "base" in which:
        specs["base"] = (cells_of(row_frame(f, y, fe_au)), dict(eta_mode="base"))
    if "D0" in which:
        est = np.where(later, np.searchsorted(E_STEPS, f["e"]), 0)
        specs["D0"] = (cells_of(row_frame(f, y, fe_au, extra_keys={"estep": est})), dict(eta_mode="steps"))
    if "D1_talk" in which:
        specs["D1_talk"] = (cells_of(row_frame(f, f["talk"].astype(float), fe_au)), dict(eta_mode="base"))
    if "D1_reptalk" in which:
        specs["D1_reptalk"] = (cells_of(row_frame(f, y, fe_au, sel=f["talk"])), dict(eta_mode="base"))
    if "D2" in which:
        pk = f["prev_kind"]
        pkc = np.select([pk == KIND.index("search"), pk == KIND.index("room_move"),
                         ~np.isin(pk, [KIND.index("cu_action"), KIND.index("talk"), KIND.index("search"),
                                       KIND.index("room_move")])], [1, 2, 3], 0)
        rf = row_frame(f, y, fe_au, extra_cont={"prev_logrows": np.log1p(f["prev_rows"])},
                       extra_keys={"prevkind": pkc, "prevfail": f["prev_fail"], "prevwrite": f["prev_write"]})
        specs["D2"] = (cells_of(rf), dict(eta_mode="base", extra_cont_later=["prev_logrows"],
                                          extra_cat_later=["prevkind", "prevfail", "prevwrite"]))
    if "D3" in which and "third" in f:
        rf = row_frame(f, y, fe_au, extra_cont={"log_nment": np.log1p(f["n_ment_n"]), "log_nhuman": np.log1p(f["n_human_n"]),
                                                "log_third": np.log1p(f["third"])},
                       extra_keys={"anyagent": f["n_agent_n"] > 0, "thirdb": np.minimum(f["third"], 2)})
        specs["D3"] = (cells_of(rf), dict(eta_mode="base", extra_cont_later=["log_nment", "log_nhuman", "log_third"],
                                          extra_cat_later=["anyagent"]))
    if "D4" in which:
        fe_adr = fe_codes(f["au"], f["day"], f["room1"])
        specs["D4"] = (cells_of(row_frame(f, y, fe_adr)), dict(eta_mode="base"))
    if "D5" in which:
        sel = f["first"] | (f["k"] == 0)
        specs["D5"] = (cells_of(row_frame(f, y, fe_au, sel=sel)), dict(eta_mode="base"))
    if "D6" in which:
        gem = np.array([X.lab.get(int(a), "?") == "Google" for a in f["recv"]])
        ok_l = later & gem & f["logged_n"] & f["logged_p"] & f["prev_is_row"] & np.isfinite(f["api_p"])
        sel = (f["first"] & gem) | ok_l
        if sel.sum() > 1000 and y[sel & later].sum() >= 20:
            api = np.where(ok_l, np.maximum(f["api_p"], 0.5), 10.0)
            rest = np.where(ok_l, np.maximum(f["e"] - f["api_p"], 0.5), 10.0)
            rf = row_frame(f, y, fe_au, sel=sel, extra_cont={"logapi": np.log(api / 10), "logrest": np.log(rest / 10)})
            specs["D6"] = (cells_of(rf), dict(eta_mode="split_api"))
            specs["D6_base"] = (cells_of(row_frame(f, y, fe_au, sel=sel)), dict(eta_mode="base"))
    return specs


def r6(goal: int, B: int, calls=None, X=None):
    t0 = time.time()
    calls = calls or L.load_calls()
    X = X or load_extra(calls.n)
    btid = L._call_tid_of_messages(calls)
    it = load_items(goal, calls, btid, with_ids=True)
    rows = expand_all(calls, it)
    rows, y = L.truncate(rows, it["r_tid"].to_numpy())
    third = third_party_counts(goal, it, rows, calls)
    f = features(rows, it, calls, X, third)
    print(f"  [G{goal}] rows {len(y)} replies {int(y.sum())} ({time.time() - t0:.0f}s)", flush=True)
    specs = r6_specs(f, y.astype(float), X)
    out = run_specs(specs, B, L.SEED + 600 + goal, coefs=("eta",))
    # descriptive context: share of later rows that talk, by span tercile (covariates and talk only, no reply outcome)
    later = ~f["first"]
    out["context"] = dict(talk_share_later=float(f["talk"][later].mean()), k0_share_later=float((f["k"][later] == 0).mean()),
                          third_any_share=float((f["third"][later] > 0).mean()), median_e=float(np.median(f["e"][later])),
                          secs=round(time.time() - t0, 1))
    R2.mkdir(parents=True, exist_ok=True)
    L.jdump(out, R2 / f"r6_G{goal:02d}.json")
    for nm, r in out.items():
        if nm == "context":
            continue
        ks = [k for k in r["coef"] if k.startswith("eta") or k.startswith("estep") or k in ("log_third", "prev_logrows")]
        print(f"  {nm:11s} y={r['n_y']:.0f} " + " ".join(f"{k}={r['coef'][k]:+.2f}[{r['ci'][k][0]:+.2f},{r['ci'][k][1]:+.2f}]" for k in ks)
              + (f" | d_eta={r['delta_eta']['est']:+.2f}[{r['delta_eta']['lo']:+.2f},{r['delta_eta']['hi']:+.2f}]" if "delta_eta" in r else ""),
              flush=True)
    return out


def sim_first_hit(rows: L.Rows, h: np.ndarray, rng, n_items: int) -> np.ndarray:
    hit = rng.random(len(h)) < h
    reply = np.full(n_items, -1, dtype=np.int64)
    hi = np.flatnonzero(hit)
    if len(hi):
        ih = rows.item[hi]
        fst = np.r_[True, ih[1:] != ih[:-1]]
        reply[ih[fst]] = rows.tid[hi[fst]]
    return reply


def calib_shift(h_fn, target, lo=-12.0, hi=4.0):
    for _ in range(36):
        mid = (lo + hi) / 2
        p = h_fn(mid)
        lo, hi = (mid, hi) if p < target else (lo, mid)
    return (lo + hi) / 2


def truth_coef(goal: int, clock: str) -> tuple[dict, np.ndarray]:
    """Real round-1 coefficients and intercepts, with the clock terms replaced (call: eta = eta1 = psi = 0; wall:
    eta = eta1 = 1, phi = 0, psi = the fitted phi). Separated gap dummies are capped at -6."""
    r = json.loads((L.OUT / "results" / f"G{goal:02d}.json").read_text())
    c = {k: max(v, -6.0) for k, v in r["coef"].items()}
    fe = np.array(r["au_table"]["fe"], dtype=float)
    fe = np.clip(fe, np.nanmedian(fe) - 4, None)
    if clock == "call":
        c.update(eta=0.0, eta1=0.0, psi=0.0)
    elif clock == "wall":
        c.update(eta=1.0, eta1=1.0, psi=c.get("phi", -0.6), phi=0.0)
    return c, fe


def r6syn(goal: int, reps: int, calls=None, X=None):
    """S1 call clock (all diagnostics must read eta ~ 0); S6 call clock only at real talk calls (reply-given-talk
    eta ~ 0); S7 as S6 with eta = -0.5 given talk; S8 call clock + detection loss when new items arrive (D5 ~ 0)."""
    calls = calls or L.load_calls()
    X = X or load_extra(calls.n)
    btid = L._call_tid_of_messages(calls)
    it = load_items(goal, calls, btid, with_ids=True)
    rng = np.random.default_rng(L.SEED + 7000 + goal)
    target = float((it["r_tid"] >= 0).mean())
    ment = it["ment"].to_numpy(); rank = it["rank"].to_numpy().astype(np.int64); aucode = it["au"].to_numpy()
    kB = third_party_keys(goal, it)
    out = []
    coef0, fe0 = truth_coef(goal, "call")
    for sc in ("S1", "S6", "S7", "S8"):
        coef = dict(coef0)
        if sc == "S7":
            coef["eta"] = -0.5
        shift = None
        for rep in range(reps):
            t0 = time.time()
            ctrue = L.with_times(calls, L.jitter_times(calls, rng))
            rows_u = expand_all(ctrue, it)            # truth rows on the jittered schedule, same read-out calls
            talk_mask = calls.talk[rows_u.tid] if sc in ("S6", "S7") else np.ones(len(rows_u.tid), bool)
            dev = rng.normal(0, 0.3, len(fe0))

            def hfun(s, coef=coef, rows_u=rows_u, talk_mask=talk_mask, dev=dev):
                eta = L.rows_linpred(rows_u, ment, rank, coef, fe0 + dev + s, aucode)
                h, _ = L._cloglog_mu(eta)
                return h * talk_mask
            if shift is None:
                shift = calib_shift(lambda s: 1 - np.exp(np.bincount(rows_u.item, weights=np.log1p(-np.minimum(hfun(s), 1 - 1e-12)),
                                                                    minlength=it.height)).mean(), target)
            h = hfun(shift)
            if sc == "S8":
                h = h * np.where(rows_u.k >= 2, 0.4, 1.0)      # detection loss when >= 2 new items arrive at the call
            reply = sim_first_hit(rows_u, h, rng, it.height)
            reply = np.where(reply < it["c1"].to_numpy(), -1, reply)
            rows = expand_all(calls, it)
            rows, y = L.truncate(rows, reply)
            f = features(rows, it, calls, X, third_party_counts(goal, it, rows, calls, kB))
            which = {"S1": ("base", "D2", "D3", "D4", "D5"), "S6": ("base", "D1_reptalk"), "S7": ("base", "D1_reptalk"),
                     "S8": ("base", "D5")}[sc]
            specs = r6_specs(f, y.astype(float), X, which=which)
            res = dict(scenario=sc, rep=rep, goal=goal, replies=float(y.sum()))
            for nm, (cells, kw) in specs.items():
                fr, _ = fit_spec(cells, **kw)
                res[f"{nm}_eta"] = fr.get("eta"); res[f"{nm}_se"] = fr.se("eta")
            res["secs"] = round(time.time() - t0, 1)
            out.append(res)
            print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()}, flush=True)
    R2.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(out).write_parquet(R2 / f"r6syn_G{goal:02d}.parquet")
    return out


# ============================================================================= R1 (regime I span split)

def r1_rows(goal: int, calls: L.Calls, X: Extra, calls_rows: L.Calls | None = None):
    """Gemini recipients' items; first rows + later rows at chat-mode calls n whose previous call is the previous risk
    row, chat-mode, and both starts logged."""
    it = load_items(goal, calls)
    gem = np.array([X.lab.get(int(a), "?") == "Google" for a in it["recv"].to_numpy()])
    it = it.filter(pl.Series(gem))
    if it.height == 0:
        return None
    cr = calls if calls_rows is None else calls_rows
    rows = expand_all(cr, it)
    rows, y = L.truncate(rows, it["r_tid"].to_numpy())
    f = features(rows, it, cr, X)
    later = ~f["first"]
    ok_l = later & f["chat"] & f["chat_p"] & f["logged_n"] & f["logged_p"] & f["prev_is_row"]
    sel = f["first"] | ok_l
    return it, rows, y.astype(float), f, sel, ok_l


def r1_specs(f, y, sel, ok_l, which=("base", "split")):
    fe_au = f["au"].astype(np.int32)
    busy = np.where(ok_l, np.maximum(f["busy_p"], 0.5), 10.0)
    wait = np.where(ok_l, np.maximum(f["wait_n"], 0.5), 10.0)
    specs = {}
    if "base" in which:
        specs["base"] = (cells_of(row_frame(f, y, fe_au, sel=sel)), dict(eta_mode="base"))
    if "split" in which:
        rf = row_frame(f, y, fe_au, sel=sel, extra_cont={"logbusy": np.log(busy / 10), "logwait": np.log(wait / 10)})
        specs["split"] = (cells_of(rf), dict(eta_mode="split_busy_wait"))
    return specs


def placed_times(calls: L.Calls, X: Extra, goals) -> np.ndarray:
    """t_call with logged chat-mode starts of the given periods replaced by t_first - the agent's median latency on
    logged chat-mode calls (the rule non-Gemini chat calls get)."""
    t = calls.t.copy()
    m = X.logged & calls.chat & np.isin(calls.goal, goals) & ~calls.holdout
    lat = X.t_first - calls.t
    for a in np.unique(calls.agent[m]):
        s = m & (calls.agent == a)
        t[s] = X.t_first[s] - np.median(lat[s])
    return t


def r1(B: int, calls=None, X=None):
    calls = calls or L.load_calls()
    X = X or load_extra(calls.n)
    cpl = L.with_times(calls, placed_times(calls, X, R1_PERIODS))
    out = {}
    for g in R1_PERIODS:
        t0 = time.time()
        r = r1_rows(g, calls, X)
        if r is None:
            continue
        it, rows, y, f, sel, ok_l = r
        res = dict(n_items=it.height, later_rows=int(ok_l.sum()), later_replies=float(y[ok_l].sum()),
                   first_replies=float(y[f["first"]].sum()),
                   busy_share=float(np.median(f["busy_p"][ok_l] / np.maximum(f["e"][ok_l], 0.05))),
                   median_e=float(np.median(f["e"][ok_l])), median_busy=float(np.median(f["busy_p"][ok_l])),
                   median_wait=float(np.median(f["wait_n"][ok_l])))
        specs = r1_specs(f, y, sel, ok_l)
        # R1c: same items, rows rebuilt on placed starts; the same call membership rule (by turn id)
        rp = expand_all(cpl, it)
        rp, yp = L.truncate(rp, it["r_tid"].to_numpy())
        fp = features(rp, it, cpl, X)
        okp = (~fp["first"]) & fp["chat"] & fp["chat_p"] & fp["logged_n"] & fp["logged_p"] & fp["prev_is_row"]
        specs["placed"] = (cells_of(row_frame(fp, yp.astype(float), fp["au"].astype(np.int32), sel=fp["first"] | okp)),
                           dict(eta_mode="base"))
        res.update(run_specs(specs, B, L.SEED + 900 + g, coefs=("eta",)))
        res["secs"] = round(time.time() - t0, 1)
        out[str(g)] = res
        b, s_, p = res["base"], res["split"], res["placed"]
        print(f"G{g}: later rows {res['later_rows']} replies {res['later_replies']:.0f} | eta {b['coef'].get('eta', np.nan):+.2f}"
              f"±{b['se'].get('eta', np.nan):.2f} | busy {s_['coef'].get('eta_busy', np.nan):+.2f}±{s_['se'].get('eta_busy', np.nan):.2f}"
              f" wait {s_['coef'].get('eta_wait', np.nan):+.2f}±{s_['se'].get('eta_wait', np.nan):.2f} | placed "
              f"{p['coef'].get('eta', np.nan):+.2f} d {p.get('delta_eta', {}).get('est', np.nan):+.2f}±{p.get('delta_eta', {}).get('se', np.nan):.2f}"
              f" ({res['secs']}s)", flush=True)
    pooled = {}
    for key, spec in (("eta", "base"), ("eta_busy", "split"), ("eta_wait", "split"), ("eta_placed", "placed")):
        k = "eta" if key in ("eta", "eta_placed") else key
        est = np.array([out[g][spec]["coef"].get(k, np.nan) for g in out])
        se = np.array([out[g][spec]["se"].get(k, np.nan) for g in out])
        pooled[key] = L.re_mean(est, se)
    est = np.array([out[g]["placed"]["delta_eta"]["est"] for g in out])
    se = np.array([out[g]["placed"]["delta_eta"]["se"] for g in out])
    pooled["delta_placed"] = L.re_mean(est, se)
    out["pooled"] = pooled
    print(json.dumps(pooled, indent=1))
    R2.mkdir(parents=True, exist_ok=True)
    L.jdump(out, R2 / "r1.json")
    return out


def r1syn(reps: int, calls=None, X=None):
    """S-eng: eta_busy = 0.6, eta_wait = 0; S-wall: eta = 1 on the total span; S-call: eta = 0. Per-period fits,
    random-effects pooled, decision rules as pre-registered."""
    calls = calls or L.load_calls()
    X = X or load_extra(calls.n)
    rng = np.random.default_rng(L.SEED + 8100)
    data = {}
    for g in R1_PERIODS:
        r = r1_rows(g, calls, X)
        if r is None:
            continue
        it, _, _, _, _, _ = r
        rows_u = expand_all(calls, it)
        fu = features(rows_u, it, calls, X)
        later = ~fu["first"]
        ok_u = later & fu["chat"] & fu["chat_p"] & fu["logged_n"] & fu["logged_p"] & fu["prev_is_row"]
        coef, fe = truth_coef(g, "call")
        data[g] = (it, rows_u, fu, ok_u, coef, fe, float((it["r_tid"] >= 0).mean()))
    out = []
    for sc in ("S-call", "S-eng", "S-wall"):
        for rep in range(reps):
            per = {}
            for g, (it, rows_u, fu, ok_u, coef, fe, target) in data.items():
                ment = it["ment"].to_numpy(); rank = it["rank"].to_numpy().astype(np.int64); aucode = it["au"].to_numpy()
                base_eta = L.rows_linpred(rows_u, ment, rank, coef, fe + rng.normal(0, 0.3, len(fe)), aucode)
                busy = np.maximum(fu["busy_p"], 0.5); wait = np.maximum(fu["wait_n"], 0.5)
                add = np.zeros(len(base_eta))
                if sc == "S-eng":
                    add = np.where(ok_u, 0.6 * np.log(busy / 10), 0.0)
                elif sc == "S-wall":
                    add = np.where(ok_u, 1.0 * np.log(rows_u.e / 10), 0.0)

                def pfun(s):
                    h, _ = L._cloglog_mu(base_eta + add + s)
                    return 1 - np.exp(np.bincount(rows_u.item, weights=np.log1p(-np.minimum(h, 1 - 1e-12)), minlength=it.height)).mean()
                s = calib_shift(pfun, target)
                h, _ = L._cloglog_mu(base_eta + add + s)
                reply = sim_first_hit(rows_u, h, rng, it.height)
                rows, y = L.truncate(rows_u, reply)
                f = features(rows, it, calls, X)
                later = ~f["first"]
                ok_l = later & f["chat"] & f["chat_p"] & f["logged_n"] & f["logged_p"] & f["prev_is_row"]
                specs = r1_specs(f, y.astype(float), f["first"] | ok_l, ok_l)
                rr = {}
                for nm, (cells, kw) in specs.items():
                    fr, _ = fit_spec(cells, **kw)
                    rr[nm] = {k: (fr.get(k), fr.se(k)) for k in ("eta", "eta_busy", "eta_wait") if k in fr.names}
                per[g] = rr
            pooled = {}
            for key, spec in (("eta", "base"), ("eta_busy", "split"), ("eta_wait", "split")):
                est = np.array([per[g][spec].get(key, (np.nan, np.nan))[0] for g in per])
                se = np.array([per[g][spec].get(key, (np.nan, np.nan))[1] for g in per])
                pooled[key] = L.re_mean(est, se)
            eng = (pooled["eta_wait"]["lo"] >= -0.25) and (pooled["eta_wait"]["hi"] <= 0.25) and (pooled["eta_busy"]["lo"] > 0)
            expo = (pooled["eta_wait"]["mean"] >= 0.3) and (pooled["eta_wait"]["lo"] > 0)
            res = dict(scenario=sc, rep=rep, eta=pooled["eta"]["mean"], eta_lo=pooled["eta"]["lo"],
                       eta_busy=pooled["eta_busy"]["mean"], eta_busy_lo=pooled["eta_busy"]["lo"],
                       eta_wait=pooled["eta_wait"]["mean"], eta_wait_lo=pooled["eta_wait"]["lo"],
                       eta_wait_hi=pooled["eta_wait"]["hi"], rule_engagement=bool(eng), rule_exposure=bool(expo))
            out.append(res)
            print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()}, flush=True)
    R2.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(out).write_parquet(R2 / "r1syn.parquet")
    return out


# ============================================================================= R5 (collapse with matched coupling)

def km_w(t, ev, w, grid):
    o = np.argsort(t, kind="stable")
    t, ev, w = t[o], ev[o], w[o]
    ut, idx = np.unique(t, return_index=True)
    tot = w.sum()
    cum_before = np.r_[0.0, np.cumsum(w)][idx]
    at_risk = tot - cum_before
    d = np.add.reduceat(w * ev, idx)
    S = np.cumprod(1 - d / np.maximum(at_risk, 1e-12))
    pos = np.searchsorted(ut, grid, side="right") - 1
    return np.where(pos >= 0, 1 - S[np.clip(pos, 0, None)], 0.0)


def collapse_w(rt: dict, terc: np.ndarray, w: np.ndarray, good: np.ndarray, r_med: float) -> dict:
    import replication as R  # same hypothesis
    wgrid = R.N_GRID * 3600.0 / r_med
    Fc = np.array([km_w(rt["tn"][good & (terc == g)], rt["ev"][good & (terc == g)], w[good & (terc == g)], R.N_GRID) for g in range(3)])
    Fw = np.array([km_w(rt["tw"][good & (terc == g)], rt["ev"][good & (terc == g)], w[good & (terc == g)], wgrid) for g in range(3)])
    with np.errstate(divide="ignore", invalid="ignore"):
        okc, okw = Fc.min(0) > 0, Fw.min(0) > 0
        Dc = float(np.nanmean(np.abs(np.log(Fc[2] / Fc[0]))[okc])) if okc.any() else np.nan
        Dw = float(np.nanmean(np.abs(np.log(Fw[2] / Fw[0]))[okw])) if okw.any() else np.nan
        lc = float(np.nanmean(np.log(Fc[2] / Fc[0])[okc])) if okc.any() else np.nan
        lw = float(np.nanmean(np.log(Fw[2] / Fw[0])[okw])) if okw.any() else np.nan
    return dict(D_call=Dc, D_wall=Dw, logratio_call=lc, logratio_wall=lw, call_better=bool(Dc < Dw) if np.isfinite(Dc + Dw) else None)


def balance_weights(strata: np.ndarray, terc: np.ndarray, good: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Weights giving every tertile the overall strata mix on common support; returns (w, good_common)."""
    g2 = good.copy()
    for s in np.unique(strata[good]):
        present = [np.any(good & (terc == t) & (strata == s)) for t in range(3)]
        if not all(present):
            g2 &= strata != s
    w = np.zeros(len(strata))
    if not g2.any():
        return w, g2
    us, inv = np.unique(strata[g2], return_inverse=True)
    p_all = np.bincount(inv) / g2.sum()
    idx = np.flatnonzero(g2)
    tt = terc[g2]
    for t in range(3):
        m = tt == t
        p_t = np.bincount(inv[m], minlength=len(us)) / max(m.sum(), 1)
        w[idx[m]] = p_all[inv[m]] / np.maximum(p_t[inv[m]], 1e-12)
    return w, g2


def r5_period(goal: int, calls: L.Calls, X: Extra, it=None, r_col="r_tid", alpha=None):
    import replication as R
    if it is None:
        it = load_items(goal, calls)
    d = L.OUT / f"G{goal:02d}"
    au = pl.read_parquet(d / "au.parquet"); cad = pl.read_parquet(d / "cadence.parquet")
    n_au = int(au["au"].max()) + 1
    rate = au.join(cad.select("agent", "unit_id", "rate"), on=["agent", "unit_id"], how="left").sort("au")
    r_au = np.full(n_au, np.nan); r_au[rate["au"].to_numpy()] = rate["rate"].to_numpy()
    ag_au = np.full(n_au, -1); ag_au[rate["au"].to_numpy()] = rate["agent"].to_numpy()
    aucode = it["au"].to_numpy()
    rate_item = r_au[aucode]
    good = np.isfinite(rate_item)
    q1, q2 = np.quantile(rate_item[good], [1 / 3, 2 / 3])
    terc = np.where(rate_item <= q1, 0, np.where(rate_item <= q2, 1, 2))
    r_med = float(np.median(rate_item[good]))
    lab_item = np.array([X.lab.get(int(a), "?") for a in ag_au[aucode]])
    _, lab_code = np.unique(lab_item, return_inverse=True)
    res = {}
    for oc in ([r_col] if r_col != "r_tid" else ["r_tid", "any_tid"]):
        rt = R.reply_timing(calls, it, tid_col=oc)
        rr = dict(raw=collapse_w(rt, terc, np.ones(len(terc)), good, r_med))
        w, g2 = balance_weights(lab_code, terc, good)
        rr["lab"] = collapse_w(rt, terc, w, g2, r_med) | dict(items_kept=float(g2.mean()), labs_kept=int(len(np.unique(lab_code[g2]))))
        if alpha is not None:
            a_item = alpha[aucode]
            okA = good & np.isfinite(a_item)
            qa = np.nanquantile(a_item[okA], [1 / 3, 2 / 3])
            ab = np.where(a_item <= qa[0], 0, np.where(a_item <= qa[1], 1, 2))
            w, g3 = balance_weights(ab, terc, okA)
            rr["alpha"] = collapse_w(rt, terc, w, g3, r_med) | dict(items_kept=float(g3.mean()))
        res[oc] = rr
    res["tertile_rates"] = [float(np.median(rate_item[good & (terc == g)])) for g in range(3)]
    return res, terc, aucode


def pool_sizes(goal: int, calls: L.Calls, it: pl.DataFrame, terc: np.ndarray) -> dict:
    """Mean DQ2 pool size (candidate parents visible) of the recipients' own reply messages, by cadence tertile;
    and the share of replying messages with > 1 labelled parent."""
    bm = pl.read_parquet(L.SH / "reply_threading/b_meta_ledger.parquet", columns=["b", "b_agent", "n_pool", "goal_no", "holdout"])
    bm = bm.filter((pl.col("goal_no") == goal) & ~pl.col("holdout"))
    tmap = pl.DataFrame({"b_agent": it["recv"].cast(pl.Int8).to_numpy(), "terc": terc}).group_by("b_agent").agg(pl.col("terc").mode().first())
    j = bm.join(tmap, on="b_agent", how="inner")
    return {str(int(t)): float(j.filter(pl.col("terc") == t)["n_pool"].mean() or np.nan) for t in range(3)}


def r5(calls=None, X=None):
    calls = calls or L.load_calls()
    X = X or load_extra(calls.n)
    bs = pl.read_parquet(L.OUT / "build_summary.parquet").filter(pl.col("eligible"))
    out = {}
    for g in bs["goal"].to_list():
        r = json.loads((L.OUT / "results" / f"G{g:02d}.json").read_text())
        alpha = np.array([np.nan if (x is None or rp < 5) else x for x, rp in zip(r["au_table"]["fe"], r["au_table"]["replies"])], dtype=float)
        it = load_items(g, calls)
        res, terc, _ = r5_period(g, calls, X, it=it, alpha=alpha)
        res["pool_by_tertile"] = pool_sizes(g, calls, it, terc)
        res["regime"] = r["regime"]
        out[str(g)] = res
        p, m = res["r_tid"], res["any_tid"]
        print(f"G{g:02d} ({r['regime']}) raw {p['raw']['D_call']:.2f}/{p['raw']['D_wall']:.2f} lab {p['lab']['D_call']:.2f}/"
              f"{p['lab']['D_wall']:.2f} alpha {p['alpha']['D_call']:.2f}/{p['alpha']['D_wall']:.2f} | multi lab "
              f"{m['lab']['D_call']:.2f}/{m['lab']['D_wall']:.2f} | pool {res['pool_by_tertile']}", flush=True)
    R2.mkdir(parents=True, exist_ok=True)
    L.jdump(out, R2 / "r5.json")
    return out


def r5syn(goal: int, reps: int, unit: str | None = None, calls=None, X=None):
    """Collapse validity: real coefficients and real intercepts under the call clock and the wall clock."""
    calls = calls or L.load_calls()
    X = X or load_extra(calls.n)
    it = load_items(goal, calls)
    if unit:
        it = it.filter(pl.col("unit_id") == unit).drop("item").with_row_index("item")
    rng = np.random.default_rng(L.SEED + 9100 + goal)
    target = float((it["r_tid"] >= 0).mean())
    ment = it["ment"].to_numpy(); rank = it["rank"].to_numpy().astype(np.int64); aucode = it["au"].to_numpy()
    out = []
    for clock in ("call", "wall"):
        coef, fe = truth_coef(goal, clock)
        shift = None
        for rep in range(reps):
            ctrue = L.with_times(calls, L.jitter_times(calls, rng))
            rows_u = expand_all(ctrue, it)
            dev = rng.normal(0, 0.1, len(fe))

            def pfun(s, rows_u=rows_u, dev=dev):
                h, _ = L._cloglog_mu(L.rows_linpred(rows_u, ment, rank, coef, fe + dev + s, aucode))
                return 1 - np.exp(np.bincount(rows_u.item, weights=np.log1p(-np.minimum(h, 1 - 1e-12)), minlength=it.height)).mean()
            if shift is None:
                shift = calib_shift(pfun, target)
            h, _ = L._cloglog_mu(L.rows_linpred(rows_u, ment, rank, coef, fe + dev + shift, aucode))
            reply = sim_first_hit(rows_u, h, rng, it.height)
            reply = np.where(reply < it["c1"].to_numpy(), -1, reply)
            it2 = it.with_columns(pl.Series("sim_tid", reply))
            res, _, _ = r5_period(goal, calls, X, it=it2, r_col="sim_tid")
            rr = res["sim_tid"]
            out.append(dict(goal=goal, unit=unit or "all", clock=clock, rep=rep, raw_call_better=rr["raw"]["call_better"],
                            lab_call_better=rr["lab"]["call_better"], raw_Dc=rr["raw"]["D_call"], raw_Dw=rr["raw"]["D_wall"],
                            lab_Dc=rr["lab"]["D_call"], lab_Dw=rr["lab"]["D_wall"], replies=float((reply >= 0).sum())))
            print(out[-1], flush=True)
    R2.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(out).write_parquet(R2 / f"r5syn_G{goal:02d}{'_' + unit if unit else ''}.parquet")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["r6", "r6syn", "r1", "r1syn", "r5", "r5syn"])
    ap.add_argument("--period", type=int, nargs="*")
    ap.add_argument("--unit", default=None)
    ap.add_argument("--B", type=int, default=50)
    ap.add_argument("--reps", type=int, default=10)
    a = ap.parse_args()
    calls = L.load_calls()
    X = load_extra(calls.n)
    if a.cmd == "r6":
        for g in a.period:
            r6(g, a.B, calls, X)
    elif a.cmd == "r6syn":
        for g in a.period:
            r6syn(g, a.reps, calls, X)
    elif a.cmd == "r1":
        r1(a.B, calls, X)
    elif a.cmd == "r1syn":
        r1syn(a.reps, calls, X)
    elif a.cmd == "r5":
        r5(calls, X)
    elif a.cmd == "r5syn":
        for g in a.period:
            r5syn(g, a.reps, a.unit, calls, X)
    L.write_provenance(f"round2_{a.cmd}", "hypotheses/H40-call-clock-coupling/analysis/round2.py",
                       ["call_windows", "context_ledger_turns", "calls", "reply_pairs", "reply_threading/b_meta_ledger",
                        "chat_core", "roster", "period_units"], dict(B=a.B, reps=a.reps, periods=a.period))


if __name__ == "__main__":
    main()
