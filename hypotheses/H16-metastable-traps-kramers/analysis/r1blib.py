"""H16 round 1b inputs (improved data, 2026-10-04). Imported by scheme/build.py --r1b and analysis/run_period.py --r1b.

  load_rows_r1b   h16lib.load_rows with `turn_err` = real failure: turn_outcomes.failed for bash/type turns, a platform
                  failure (error_class in timeout/vm/resource/network/tool_use/other) for other computer-use turns.
                  Round 1 used actions.error (stderr non-empty).
  load_kicks_r1b  h16lib.load_kicks with N_tgt = the nudge's leading-@ agent (H35) and every other exposure to a
                  nudge (including being named second) as N_by. Nudges = kicks_classified kind 'nudge'. Message text is
                  read in memory only, to find the leading @; it is never stored.
  build_window_traps   TS5 (p_blocked >= 0.5) and TS6 (longest_run >= 5) spells on Jev v3.1 in-span windows.
  dwell_windows   per-window discrete hazard (cloglog, agent FE) on ln(windows elapsed) for spells reaching 2 windows.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import h16lib as L  # noqa: E402

ROOT = L.ROOT
SH = L.SH
TO = ROOT / "data/processed/behavior_states/turn_outcomes.parquet"
PLATFORM_FAIL = ["timeout", "vm", "resource", "network", "tool_use", "other"]
BLOCK_THR = 0.5
LOOP_THR = 5


# ============================================================================ real failures
def load_rows_r1b(days, allow_holdout=False):
    rows = L.load_rows(days, allow_holdout=allow_holdout)
    ok = L._roster_ok()
    a = pl.read_parquet(SH / "actions.parquet", columns=["t", "agent", "action"]).with_row_index("row")
    b = pl.read_parquet(SH / "actions_bash_head_fixed.parquet", columns=["row", "error_class"])
    a = a.join(b, on="row", how="left").filter(pl.col("agent").is_not_null() & pl.col("agent").is_in(list(ok)))
    a = (a.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
         .filter(pl.col("pt_date").is_in(days) & (pl.col("action").cast(pl.Utf8) != "pause")))
    to = pl.read_parquet(TO, columns=["t", "agent", "failed"]).unique(["agent", "t"], keep="first")
    a = a.join(to, on=["agent", "t"], how="left")
    a = a.with_columns(
        pl.when(pl.col("action").cast(pl.Utf8).is_in(["bash", "type"])).then(pl.col("failed").fill_null(False))
        .otherwise(pl.col("error_class").cast(pl.Utf8).is_in(PLATFORM_FAIL).fill_null(False)).alias("fail_real"),
        (pl.col("t").dt.epoch("us") / 1e6).alias("ts"))
    n_set, n_turns = 0, 0
    for (ag, d), g in a.group_by(["agent", "pt_date"]):
        key = (int(ag), d)
        if key not in rows or len(rows[key]["turn_t"]) == 0:
            continue
        g = g.sort("ts")
        tt = rows[key]["turn_t"]
        ts = g["ts"].to_numpy()
        fr = g["fail_real"].to_numpy()
        # align by time (same rows, same filter; searchsorted guards against order ties)
        idx = np.searchsorted(ts, tt)
        idx = np.clip(idx, 0, len(ts) - 1)
        assert np.allclose(ts[idx], tt), "turn alignment failed"
        rows[key]["turn_err"] = fr[idx].astype(bool)
        n_set += int(fr[idx].sum())
        n_turns += len(tt)
    return rows


# ============================================================================ leading-@ nudge targets
def nudge_targets(days, allow_holdout=False):
    """Nudge messages on `days` with the leading-@ target (agent code or null). No text kept."""
    import common  # infra/shared (on sys.path via h16lib's ROOT)
    if not allow_holdout:
        L.assert_no_holdout(days)
    kc = pl.read_parquet(SH / "kicks_classified.parquet", columns=["message_id", "kind", "pt_date", "t"]).filter(
        (pl.col("kind").cast(pl.Utf8) == "nudge") & pl.col("pt_date").is_in(days))
    if kc.height == 0:
        return pl.DataFrame(schema={"message_id": pl.Utf8, "target": pl.Int16, "ts": pl.Float64})
    txt = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).filter(
        pl.col("message_id").is_in(kc["message_id"].implode()))
    kc = kc.join(txt, on="message_id", how="left")
    ros = pl.read_parquet(SH / "roster.parquet").filter(~pl.col("claude_code"))
    agents = [{"id": int(x), "name": n} for x, n in ros.select("agent", "name").iter_rows()]
    pats = common.mention_regexes(agents)
    span = {int(x): (j, l) for x, j, l in ros.select("agent", "joined", "left").iter_rows()}
    tgt = []
    for d, text in kc.select("pt_date", "text").iter_rows():
        best, blen = None, 0
        if text and text.startswith("@"):
            for ag, pat in pats.items():
                j, l = span[ag]
                if not (j <= d and (l is None or d < l)):
                    continue
                m = pat.match(text, 1)
                if m and (m.end() - m.start()) > blen:
                    best, blen = ag, m.end() - m.start()
        tgt.append(best)
    return kc.with_columns(pl.Series("target", tgt, dtype=pl.Int16), (pl.col("t").dt.epoch("us") / 1e6).alias("ts")).select(
        "message_id", "target", "ts")


def load_kicks_r1b(days, allow_holdout=False):
    if str(ROOT / "infra/shared") not in sys.path:
        sys.path.insert(0, str(ROOT / "infra/shared"))
    K = L.load_kicks(days, allow_holdout=allow_holdout)
    for a in K:
        K[a].pop("N_tgt", None)
        K[a].pop("N_by", None)
    nud = nudge_targets(days, allow_holdout=allow_holdout)
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg")
    ids = chat.filter(pl.col("message_id").is_in(nud["message_id"].implode()))
    ex = (pl.read_parquet(SH / "exposure.parquet", columns=["msg", "agent"]).join(ids, on="msg", how="inner")
          .join(nud, on="message_id", how="inner"))
    by = ex.filter(pl.col("agent").cast(pl.Int16) != pl.col("target").fill_null(-1))
    for (a,), g in by.group_by(["agent"]):
        K.setdefault(int(a), {})["N_by"] = np.sort(g["ts"].to_numpy())
    for (a,), g in nud.drop_nulls("target").group_by(["target"]):
        K.setdefault(int(a), {})["N_tgt"] = np.sort(g["ts"].to_numpy())
    return K, {"nudges": nud.height, "with_leading_target": int(nud["target"].is_not_null().sum())}


# ============================================================================ v3 window traps
def build_window_traps(days, K, kind, allow_holdout=False):
    """TS5 (kind='blocked') / TS6 (kind='loop'): one row per spell window from the 2nd... onwards rows for all k >= 1.

    Spell = consecutive labelled in-span windows with the flag. Row k (1-based windows elapsed in the spell):
    y = 1 if the next window is consecutive, labelled and without the flag (escape); censored if the next window is
    missing, unlabelled (absent) or the span ends."""
    v = pl.read_parquet(SH / "behavior_states_v3.parquet").filter(pl.col("in_span") & pl.col("pt_date").is_in(days))
    if not allow_holdout:
        v = v.filter(~pl.col("holdout"))
        L.assert_no_holdout(sorted(v["pt_date"].unique().to_list()))
    v = v.sort("agent", "pt_date", "w")
    flag = (pl.col("p_blocked") >= BLOCK_THR) if kind == "blocked" else (pl.col("longest_run") >= LOOP_THR)
    v = v.with_columns((pl.col("labeled") & flag.fill_null(False)).alias("f"))
    ag = v["agent"].to_numpy()
    dy = v["pt_date"].to_numpy()
    w = v["w"].to_numpy()
    f = v["f"].to_numpy()
    labd = v["labeled"].to_numpy()
    t0 = (v["t0"].dt.epoch("us") / 1e6).to_numpy()
    t1 = (v["t1"].dt.epoch("us") / 1e6).to_numpy()
    n = len(f)
    nxt_ok = np.r_[(ag[1:] == ag[:-1]) & (dy[1:] == dy[:-1]) & (w[1:] - w[:-1] == 1), False]
    prev_ok = np.r_[False, nxt_ok[:-1]]
    k = np.zeros(n, int)
    for i in range(n):
        if f[i]:
            k[i] = k[i - 1] + 1 if (i > 0 and prev_ok[i] and f[i - 1]) else 1
    sel = np.flatnonzero(f)
    nf = np.r_[f[1:], False]
    nl = np.r_[labd[1:], False]
    y = nxt_ok[sel] & nl[sel] & ~nf[sel]
    cont = nxt_ok[sel] & nf[sel]
    cens = ~y & ~cont
    run_start = np.zeros(n, int)
    for i in range(n):
        run_start[i] = i if k[i] <= 1 else run_start[i - 1]
    rec = {"agent": ag[sel].astype(np.int16), "pt_date": dy[sel], "k": k[sel].astype(np.int16), "y": y.astype(np.int8),
           "censored": cens, "run": run_start[sel].astype(np.int32), "t0": t0[sel]}
    for cl in L.KCLASSES:
        rec[f"n_{cl}"] = np.zeros(len(sel), np.int16)
    for a in np.unique(ag[sel]):
        m = ag[sel] == a
        kc = L.kick_counts(K, int(a), t0[sel][m], t1[sel][m])
        for cl in L.KCLASSES:
            rec[f"n_{cl}"][m] = kc[cl]
    return pl.DataFrame(rec)


def dwell_windows(tw, rng, B=100, kmin=2):
    """Aging test for window spells: cloglog break hazard on ln k (k >= kmin), agent FE, day-bootstrap CI."""
    sys.path.insert(0, str(HERE))
    from run_period import verdict_slope  # noqa: E402
    if tw.height < 30:
        return {"ok": False, "n": tw.height}
    g = tw.filter(~pl.col("censored"))
    k = g["k"].to_numpy().astype(float)
    y = g["y"].to_numpy()
    out = {"ok": True, "n_rows": g.height, "n_spells": int(tw.filter(pl.col("k") == 1).height),
           "censored_frac": float(tw["censored"].mean()),
           "p_break_by_k": [{"k": kk, "n": int((np.minimum(k, 8) == kk).sum()),
                             "p": float(y[np.minimum(k, 8) == kk].mean()) if (np.minimum(k, 8) == kk).any() else np.nan} for kk in range(1, 9)]}
    m = k >= kmin
    if y[m].sum() < 15:
        out["deep"] = {"ok": False, "events": int(y[m].sum())}
        return out
    X = np.log(k[m])[:, None]
    f = L.glm_fe(y[m], X, g["agent"].to_numpy()[m], "cloglog")
    fp = L.glm_fe(y[m], X, None, "cloglog")
    days = np.array(g["pt_date"].to_list())[m]
    bs = []
    for idx in L.day_bootstrap(days, rng, B):
        bs.append(L.glm_fe(y[m][idx], X[idx], g["agent"].to_numpy()[m][idx], "cloglog")["beta"][0])
    bs = np.array(bs, float)
    bs = bs[np.isfinite(bs)]
    ci = (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))) if len(bs) > 10 else (np.nan, np.nan)
    b0, se = float(f["beta"][0]), float(f["se"][0])
    out["deep"] = {"ok": True, "beta_agentFE": b0, "se": se, "ci": list(ci), "ci_wald": [b0 - 1.96 * se, b0 + 1.96 * se],
                   "beta_pooled": float(fp["beta"][0]), "events": f["n_events"], "verdict": verdict_slope(b0, *ci),
                   "verdict_wald": verdict_slope(b0, b0 - 1.96 * se, b0 + 1.96 * se)}
    # directed / undirected kicks in the window (descriptive)
    gd = np.sum([g[f"n_{c}"].to_numpy() for c in ("A_men", "H_men", "N_tgt")], axis=0)
    gu = np.sum([g[f"n_{c}"].to_numpy() for c in ("A_und", "H_und")], axis=0)
    Xk = np.stack([np.log(k), (gd > 0).astype(float), (gu > 0).astype(float)], 1)
    fk = L.glm_fe(y, Xk, g["agent"].to_numpy(), "cloglog")
    out["kicks"] = {"directed_lnHR": float(fk["beta"][1]), "directed_se": float(fk["se"][1]), "directed_rows": int((gd > 0).sum()),
                    "undirected_lnHR": float(fk["beta"][2]), "undirected_se": float(fk["se"][2]), "undirected_rows": int((gu > 0).sum())}
    return out
