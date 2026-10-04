"""H40 POST HOC (after the first replication results): is the positive eta of chat-mode (latency-placed) calls a
start-time artifact?

Latency-placed call starts (start_conf low: regime-I/II chat-mode calls, first calls of a day, early wakes) are
t_first minus the agent's median latency. A call that takes longer to generate its first record (a long reply) is then
placed too late, which lengthens its own span e exactly at reply calls and can manufacture eta > 0. Logged starts
(Gemini, from 2025-12-19; start_conf high) and chained computer-use starts (previous end + 1.7 s; medium) do not depend
on the call's own generation time.

Test: refit the hazard model with log e interacted with the start source of the call (low / medium / high) and with
call mode. If the artifact explains it, eta on low-confidence calls > 0 while eta on logged (high) calls ~ 0, including
logged chat-mode calls of the Gemini agents in #23-#31.

  uv run python hypotheses/H40-call-clock-coupling/analysis/posthoc_conf.py --period 23 24 25 26 27 30 31 33 35 ...
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h40lib as L  # noqa: E402

OUTD = L.OUT / "posthoc"


def cells_conf(calls: L.Calls, it: pl.DataFrame) -> pl.DataFrame:
    """Cells with an extra key: start confidence of the call (0 low, 1 medium, 2 high) stored in the 'reset' slot? No:
    a separate aggregation with conf folded into 'gap' (gap*3 + conf) to keep the cell schema."""
    c1 = it["c1"].to_numpy(); t_m = it["t_m"].to_numpy(); rank = it["rank"].to_numpy().astype(np.int64)
    ment = it["ment"].to_numpy().astype(np.int64); day = it["day"].to_numpy(); aucode = it["au"].to_numpy()
    rt = it["r_tid"].to_numpy()
    parts = []
    for dd in np.unique(day):
        s = np.flatnonzero(day == dd)
        rows = L.expand(calls, c1[s], t_m[s], rank[s])
        rows.item = s[rows.item]
        rows, y = L.truncate(rows, rt)
        conf = calls.conf[rows.tid].astype(np.int64)
        # confidence of the span: the lower of this call's and the previous risk-set call's start confidence
        first = rows.n == 1
        prev_tid = np.r_[rows.tid[:1], rows.tid[:-1]]
        conf_span = np.where(first, conf, np.minimum(conf, calls.conf[prev_tid]))
        rows.gap = (rows.gap.astype(np.int64) * 3 + conf_span).astype(np.int16)   # 6 gaps x 3 conf < 2^5
        parts.append(L.aggregate(rows, y.astype(float), day, aucode, ment, rank))
    return L.merge_cells(parts)


def design_conf(cells: pl.DataFrame, n_au: int):
    """Full spec with gap main effects, plus log e interacted with span confidence and chat mode."""
    gapc = cells["gap"].to_numpy()
    gap, conf = gapc // 3, gapc % 3
    c2 = cells.with_columns(pl.Series("gap", gap.astype(np.int16)))
    FE, Xm, off, names = L.design(c2, L.SPEC_FULL, n_au=n_au)
    N = cells["N"].to_numpy()
    loge = cells["s_loge"].to_numpy() / np.maximum(N, 1e-12)
    later = (cells["nb"].to_numpy() > 0).astype(float)
    chat = cells["chat"].to_numpy().astype(float)
    extra, en = [], []
    for k, nm in ((0, "low"), (2, "high")):          # medium (chained) is the reference slope 'eta'
        m = (conf == k).astype(float)
        if (later * m).sum() > 0:
            extra.append(later * m); en.append(f"conf_{nm}")
            extra.append(later * m * loge); en.append(f"eta_x_conf_{nm}")
    if chat.any():
        extra.append(later * chat * loge); en.append("eta_x_chat")
    return FE, np.column_stack([Xm] + extra), off, names + en


def run(goal: int, calls: L.Calls) -> dict:
    d = L.OUT / f"G{goal:02d}"
    it = pl.read_parquet(d / "items.parquet")
    n_au = int(pl.read_parquet(d / "au.parquet")["au"].max()) + 1
    cells = cells_conf(calls, it)
    FE, Xm, off, names = design_conf(cells, n_au)
    f, _ = L.fit(FE, Xm, off, cells["y"].to_numpy(), cells["N"].to_numpy())
    f.names = names

    def comb(*nms):
        idx = [names.index(n) for n in nms if n in names]
        if len(idx) < len(nms):
            return None
        est = float(sum(f.beta[i] for i in idx))
        v = sum(f.cov[i, j] for i in idx for j in idx)
        se = float(np.sqrt(max(v, 0)))
        return dict(est=est, se=se, lo=est - 1.96 * se, hi=est + 1.96 * se)
    gapc = cells["gap"].to_numpy()
    later = cells["nb"].to_numpy() > 0
    cnt = {}
    for k, nm in ((0, "low"), (1, "medium"), (2, "high")):
        m = later & (gapc % 3 == k)
        cnt[nm] = dict(replies=float(cells["y"].to_numpy()[m].sum()), rows=float(cells["N"].to_numpy()[m].sum()),
                       chat_replies=float(cells["y"].to_numpy()[m & (cells["chat"].to_numpy() == 1)].sum()))
    out = dict(goal=goal, counts=cnt,
               eta_medium_cu=comb("eta"), eta_low_cu=comb("eta", "eta_x_conf_low"), eta_high_cu=comb("eta", "eta_x_conf_high"),
               eta_low_chat=comb("eta", "eta_x_conf_low", "eta_x_chat"), eta_high_chat=comb("eta", "eta_x_conf_high", "eta_x_chat"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, nargs="+", required=True)
    a = ap.parse_args()
    calls = L.load_calls()
    OUTD.mkdir(parents=True, exist_ok=True)
    res = {}
    for g in a.period:
        r = run(g, calls)
        res[f"G{g:02d}"] = r
        fmt = lambda x: "n/a" if x is None else f"{x['est']:+.2f}±{x['se']:.2f}"  # noqa: E731
        print(f"G{g:02d} counts {r['counts']} | medium(cu) {fmt(r['eta_medium_cu'])} low(cu) {fmt(r['eta_low_cu'])} "
              f"high(cu) {fmt(r['eta_high_cu'])} | low(chat) {fmt(r['eta_low_chat'])} high(chat) {fmt(r['eta_high_chat'])}", flush=True)
    prev = OUTD / "conf_split.json"
    import json
    old = json.loads(prev.read_text()) if prev.exists() else {}
    old.update(res)
    L.jdump(old, prev)


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------------- POST HOC 2: unlogged calls?
# If some regime-I calls are not logged (H08 known issue), a long apparent span e hides extra calls, and the per-observed-
# call hazard grows with e even under a pure call clock. Check: refit with later rows restricted to short spans
# (e < 128 s, about two scheduler periods of ~74 s), where a hidden call is unlikely, and compare eta (CU) and eta_chat.

def short_span(goals, e_bin_max: int = 6) -> dict:
    out = {}
    for g in goals:
        d = L.OUT / f"G{g:02d}"
        cells = pl.read_parquet(d / "cells.parquet")
        n_au = int(pl.read_parquet(d / "au.parquet")["au"].max()) + 1
        res = {}
        for tag, c in (("all", cells), ("short", cells.filter((pl.col("nb") == 0) | (pl.col("eb") <= e_bin_max)))):
            f, _ = L.fit_cells(c, L.SPEC_GAP, n_au=n_au)
            ec = None
            if "eta_x_chat" in f.names:
                i, j = f.names.index("eta"), f.names.index("eta_x_chat")
                est = f.beta[i] + f.beta[j]
                se = float(np.sqrt(f.cov[i, i] + f.cov[j, j] + 2 * f.cov[i, j]))
                ec = dict(est=float(est), se=se)
            res[tag] = dict(eta_cu=dict(est=f.get("eta"), se=f.se("eta")), eta_chat=ec,
                            replies_later=float(c.filter(pl.col("nb") > 0)["y"].sum()))
        out[f"G{g:02d}"] = res
        fmt = lambda x: "n/a" if x is None else f"{x['est']:+.2f}±{x['se']:.2f}"  # noqa: E731
        print(f"G{g:02d} all: cu {fmt(res['all']['eta_cu'])} chat {fmt(res['all']['eta_chat'])} | "
              f"e<128s: cu {fmt(res['short']['eta_cu'])} chat {fmt(res['short']['eta_chat'])} "
              f"(later replies {res['all']['replies_later']:.0f} -> {res['short']['replies_later']:.0f})", flush=True)
    return out


if __name__ == "__main__" and "--short-span" in sys.argv:
    pass
