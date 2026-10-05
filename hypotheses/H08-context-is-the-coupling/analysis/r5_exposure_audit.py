"""H08 round 2, R5: exposure audit (stale or replayed input feeds) and a log-free decoupling monitor.

  uv run python hypotheses/H08-context-is-the-coupling/analysis/r5_exposure_audit.py synth    # guard for the monitor
  uv run python hypotheses/H08-context-is-the-coupling/analysis/r5_exposure_audit.py real

R5-a  fetch-log audit of the Claude Code agent (cc/cc_fetches, cc/cc_seen, cc/cc_village_events; reserved days were
      dropped when those were built): per fetch, the share of returned events created > 24 h before the fetch (stale),
      freshness lag (fetch - newest returned event); decoupled episode = >= 3 consecutive stale fetches (fetches with
      events); monitor = median age of returned events over the last 5 fetches > 1 h.
R5-a' status audit (r2/cc_status.parquet): goal shown vs goal active; day fields.
R5-b  log-free monitor M(agent-day) = mean_s [cos(s, c30(s)) - cos(s, c30_shift(s))]; c30 = normalized centroid of
      other speakers' messages in the agent's room (room rule) in the 30 min before s; c30_shift = the same offset from
      the day's window start on up to 3 other non-reserved days of the period (mean). Flag: >= 10 statements and the 95%
      bootstrap lower bound of M <= 0. Power floor: expected flags if each agent-day had its agent-period median M
      (normal approximation with the day's own SE).
R5-c  ledger `omitted` share (beyond the 200-event cap) of received agent messages, per period.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from h08lib import *  # noqa: E402,F403
from build_turns_ledger import chat_full, period_days_any  # noqa: E402
from build_turns import room_lookup, room_at  # noqa: E402
from scipy.stats import norm as N01  # noqa: E402

OUT2 = OUT / "r2"
CC = OUT / "cc"
STALE_S = 86400
W30 = 30 * 60 * US
MODELS = {"bge": "chat_bge_small.npy", "gte": "chat_gte_modernbert.npy"}
REPLAY_START = "2026-03-17"
B = 200


# ----------------------------------------------------------------------------- R5-a
def fetch_audit():
    fe = pl.read_parquet(CC / "cc_fetches.parquet").sort("t_result")
    se = pl.read_parquet(CC / "cc_seen.parquet")
    ev = pl.read_parquet(CC / "cc_village_events.parquet", columns=["event_id", "t"])
    se = se.join(ev, on="event_id", how="left").with_columns(
        pl.coalesce(pl.col("t"), pl.col("t_event_api").dt.cast_time_unit("us")).alias("t_any"))
    se = se.join(fe.select("fetch_id", "t_result"), on="fetch_id", how="inner").with_columns(
        ((pl.col("t_result") - pl.col("t_any")).dt.total_microseconds() / US).alias("age_s"))
    pf = (se.group_by("fetch_id").agg(pl.len().alias("n_ev"), (pl.col("age_s") > STALE_S).mean().alias("stale_share"),
                                      pl.col("age_s").min().alias("fresh_lag_s"), pl.col("age_s").median().alias("med_age_s"))
          .join(fe.select("fetch_id", "t_result", "session"), on="fetch_id").sort("t_result"))
    pf = pf.with_columns(pl.col("t_result").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"),
                         (pl.col("stale_share") >= 0.5).alias("stale"))
    t = us(pf["t_result"]); stale = pf["stale"].to_numpy(); days = pf["pt_date"].to_list()
    # episodes: maximal runs of >= 3 consecutive stale fetches
    eps = []
    i = 0
    while i < len(stale):
        if stale[i]:
            j = i
            while j + 1 < len(stale) and stale[j + 1]:
                j += 1
            if j - i + 1 >= 3:
                gaps = np.diff(t[i:j + 1]) / US
                eps.append({"start": str(pf["t_result"][i]), "end": str(pf["t_result"][j]), "n_fetches": int(j - i + 1),
                            "start_day": days[i], "end_day": days[j], "n_days": len(set(days[i:j + 1])),
                            "active_h": float(gaps[gaps <= 1800].sum() / 3600)})
            i = j + 1
        else:
            i += 1
    # within the replay span: share stale
    span = pf.filter(pl.col("pt_date") >= REPLAY_START)
    pre = pf.filter(pl.col("pt_date") < REPLAY_START)
    # monitor: rolling median age over the last 5 fetches > 1 h
    med = pf["med_age_s"].to_numpy()
    roll = np.array([np.median(med[max(0, k - 4):k + 1]) for k in range(len(med))])
    alarm = roll > 3600
    out = {"n_fetches_with_events": pf.height, "n_days": len(set(days)), "episodes": eps,
           "replay_span": {"n": span.height, "stale_share": float(span["stale"].mean()) if span.height else None,
                           "median_fresh_lag_s": float(span["fresh_lag_s"].median()) if span.height else None},
           "pre_span": {"n": pre.height, "stale_share": float(pre["stale"].mean()) if pre.height else None,
                        "median_fresh_lag_s": float(pre["fresh_lag_s"].median()) if pre.height else None,
                        "max_run_stale": int(max((len(list(g)) for k_, g in __import__("itertools").groupby(pre["stale"].to_list()) if k_),
                                                 default=0))}}
    # detection delay: first alarm at or after the first episode's onset, in active hours; false alarms before onset
    if eps:
        t_on = int(dt.datetime.fromisoformat(eps[0]["start"]).timestamp() * US)
        k_on = int(np.searchsorted(t, t_on))
        ka = [k for k in range(k_on, len(t)) if alarm[k]]
        if ka:
            gaps = np.diff(t[k_on:ka[0] + 1]) / US
            out["monitor"] = {"first_alarm": str(pf["t_result"][ka[0]]), "delay_fetches": int(ka[0] - k_on),
                              "delay_active_h": float(gaps[gaps <= 1800].sum() / 3600),
                              "false_alarm_fetches_before_onset": int(alarm[:k_on].sum()),
                              "false_alarm_days_before_onset": sorted({days[k] for k in range(k_on) if alarm[k]})}
    pf.write_parquet(OUT2 / "cc_fetch_audit.parquet", compression="zstd")
    per_day = pf.group_by("pt_date").agg(pl.len().alias("n"), pl.col("stale").mean().alias("stale_share"),
                                         pl.col("fresh_lag_s").median().alias("med_fresh_lag_s")).sort("pt_date")
    out["per_day"] = per_day.to_dicts()
    return out


def status_audit():
    st = pl.read_parquet(OUT2 / "cc_status.parquet")
    st = st.with_columns((pl.col("pt_date") >= REPLAY_START).alias("replay_span"))
    out = {}
    for lab, sub in (("pre", st.filter(~pl.col("replay_span"))), ("replay_span", st.filter(pl.col("replay_span")))):
        g = sub.filter(pl.col("goal_shown").is_not_null())
        out[lab] = {"n_status": sub.height, "n_goal": g.height,
                    "goal_match_share": float((g["goal_shown"] == g["goal_active"]).mean()) if g.height else None,
                    "goal_unmatched_text_share": float((g["goal_shown"] == -1).mean()) if g.height else None,
                    "memory_age_median_h": float(sub["memory_age_s"].drop_nulls().median() / 3600) if sub["memory_age_s"].drop_nulls().len() else None,
                    "day_number_values": sorted(set(sub["day_number"].drop_nulls().to_list()))[:5] + ["..."],
                    "n_village_agents_median": float(sub["n_village_agents"].drop_nulls().median()) if sub["n_village_agents"].drop_nulls().len() else None}
    days = st.group_by("pt_date").agg(pl.len().alias("n"), (pl.col("goal_shown") == pl.col("goal_active")).mean().alias("goal_match"),
                                      pl.col("day_number").drop_nulls().max().alias("day_number_max"),
                                      pl.col("day_field").drop_nulls().min().alias("day_field_min"),
                                      pl.col("day_field").drop_nulls().max().alias("day_field_max")).sort("pt_date")
    out["per_day"] = days.to_dicts()
    return out


# ----------------------------------------------------------------------------- R5-b
def monitor_frame(g, chat, tl, E, V=None, days=None):
    """Statement-level d_s = cos(s, c30) - mean_shift cos(s, c30_shift) for every agent statement of period g."""
    days = days or period_days_any(g)
    if not days:
        return None
    win = windows(days)
    C = chat.filter(pl.col("pt_date").is_in(days) & pl.col("erow").is_not_null()).sort("t")
    t = us(C["t"]); room = C["room"].to_numpy().astype(np.int16); spk = C["agent"].fill_null(-1).to_numpy().astype(np.int16)
    kind = C["speaker_kind"].cast(pl.Utf8).to_numpy()
    d = C["pt_date"].to_list()
    X = np.asarray(E[C["erow"].to_numpy()], np.float32) if V is None else V
    dix = {x: i for i, x in enumerate(days)}
    di = np.array([dix[x] for x in d])
    off = t - np.array([win[x][0] for x in d], np.int64)
    # per (day, room): sorted offsets and cumulative vectors, and per (day, room, speaker) to exclude own messages
    keyset = {}
    for k in range(len(days)):
        for r in np.unique(room[di == k]):
            ix = np.nonzero((di == k) & (room == r))[0]
            keyset[(k, int(r))] = (off[ix], np.vstack([np.zeros((1, X.shape[1])), np.cumsum(X[ix], 0)]), spk[ix], ix)

    def centroid(k, r, o_hi, excl):
        if (k, r) not in keyset:
            return None
        oo, cs, sp, ix = keyset[(k, r)]
        lo = np.searchsorted(oo, o_hi - W30, "left"); hi = np.searchsorted(oo, o_hi, "left")
        if hi <= lo:
            return None
        v = cs[hi] - cs[lo]
        own = sp[lo:hi] == excl
        if own.any():
            v = v - X[ix[lo:hi][own]].sum(0)
        if own.all():
            return None
        n = np.linalg.norm(v)
        return v / n if n > 0 else None

    rng = np.random.default_rng(g)
    rows = []
    st_idx = np.nonzero(kind == "agent")[0]
    for q in st_idx:
        a = int(spk[q]); k = int(di[q])
        r = int(room_at(tl, a, t[q:q + 1])[0]) if a in tl else int(room[q])
        if r < 0:
            r = int(room[q])
        c = centroid(k, r, off[q], a)
        if c is None:
            continue
        others = [x for x in range(len(days)) if x != k]
        if not others:
            continue
        sh = rng.choice(others, size=min(3, len(others)), replace=False)
        cs_ = [centroid(int(x), r, off[q], a) for x in sh]
        cs_ = [x for x in cs_ if x is not None]
        if not cs_:
            continue
        dval = float(X[q] @ c - np.mean([X[q] @ x for x in cs_]))
        rows.append((a, days[k], dval))
    return pl.DataFrame(rows, schema={"agent": pl.Int16, "pt_date": pl.Utf8, "d": pl.Float64}, orient="row")


def flag_days(F: pl.DataFrame, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    med = F.group_by("agent").agg(pl.col("d").mean().alias("m_agent"))   # agent-period level (statement mean)
    mm = dict(zip(med["agent"].to_list(), med["m_agent"].to_list()))
    for (a, d), sub in F.group_by(["agent", "pt_date"], maintain_order=True):
        x = sub["d"].to_numpy()
        n = len(x)
        M = float(x.mean())
        if n >= 10:
            bs = x[rng.integers(0, n, (B, n))].mean(1)
            lo = float(np.percentile(bs, 2.5))
            se = float(x.std(ddof=1) / np.sqrt(n))
            pfloor = float(N01.cdf((1.96 * se - mm[int(a)]) / se)) if se > 0 else 0.0
        else:
            lo, pfloor = None, None
        out.append((int(a), d, n, M, lo, None if lo is None else lo <= 0, pfloor))
    return pl.DataFrame(out, schema={"agent": pl.Int16, "pt_date": pl.Utf8, "n": pl.Int32, "M": pl.Float64, "lo95": pl.Float64,
                                     "flag": pl.Boolean, "p_floor": pl.Float64}, orient="row").sort("agent", "pt_date")


def max_run(flags_by_agent):
    best = 0
    for fl in flags_by_agent:
        cur = 0
        for f in fl:
            cur = cur + 1 if f else 0
            best = max(best, cur)
    return best


def summarize_flags(D: pl.DataFrame, exclude_cc=True):
    E = D.filter(pl.col("flag").is_not_null())
    if exclude_cc:
        E = E.filter(pl.col("agent") != CC_AGENT)
    if not E.height:
        return None
    runs = max_run([sub.sort("pt_date")["flag"].to_list() for _, sub in E.group_by("agent")])
    # amendment R5-A1: null distribution of the longest run under independent flags at each day's floor probability
    rng = np.random.default_rng(7)
    sims = np.zeros(1000, int)
    for _, sub in E.group_by("agent"):
        pf = sub.sort("pt_date")["p_floor"].to_numpy()
        fl = rng.random((1000, len(pf))) < pf
        best = np.zeros(1000, int); cur = np.zeros(1000, int)
        for j in range(len(pf)):
            cur = np.where(fl[:, j], cur + 1, 0); best = np.maximum(best, cur)
        sims = np.maximum(sims, best)
    run_p95 = float(np.percentile(sims, 95)); run_p = float((sims >= runs).mean())
    return {"n_agent_days": E.height, "flagged_share": float(E["flag"].mean()), "floor_share": float(E["p_floor"].mean()),
            "excess_pp": float(100 * (E["flag"].mean() - E["p_floor"].mean())), "max_consecutive_flagged_days": runs,
            "run_null_p95": run_p95, "run_null_p": run_p,
            "median_M": float(E["M"].median())}


# ----------------------------------------------------------------------------- synthetic guard (R5-b)
def synth_vectors_monitor(days, C, rng, planted: int, alpha=0.3, dim=64, tau_min=60.0, noise_sd=1.0):
    """Room fields drift (OU) per day; coupled statements add alpha * c30 of their own room (others' messages in the
    previous 30 min); the planted agent's statements use another day's field and c30 (a replayed feed). Human messages:
    field + noise. Two passes: everyone else in time order, then the planted agent."""
    win = windows(days)
    t = us(C["t"]); room = C["room"].to_numpy().astype(np.int16); spk = C["agent"].fill_null(-1).to_numpy().astype(np.int16)
    d = C["pt_date"].to_list(); dix = {x: i for i, x in enumerate(days)}; di = np.array([dix[x] for x in d])
    off = t - np.array([win[x][0] for x in d], np.int64)
    n = len(t)
    a_ = np.exp(-1 / tau_min)
    maxm = int(off.max() / (60 * US)) + 2
    fields = {}
    for k in range(len(days)):
        for r in np.unique(room):
            z = np.zeros((maxm, dim)); z[0] = rng.normal(0, 1 / np.sqrt(dim), dim)
            e = rng.normal(0, np.sqrt(1 - a_ * a_) / np.sqrt(dim), (maxm, dim))
            for q in range(1, maxm):
                z[q] = a_ * z[q - 1] + e[q]
            fields[(k, int(r))] = z
    style = {int(a): rng.normal(0, 0.5 / np.sqrt(dim), dim) for a in np.unique(spk)}
    other_day = {k: int(rng.choice([x for x in range(len(days)) if x != k])) for k in range(len(days))}
    lists = {}
    for k in range(len(days)):
        for r in np.unique(room[di == k]):
            ix = np.nonzero((di == k) & (room == r))[0]
            lists[(k, int(r))] = (ix, off[ix])
    V = np.zeros((n, dim), np.float32)
    mi = (off / (60 * US)).astype(int)
    noise = rng.normal(0, noise_sd / np.sqrt(dim), (n, dim))

    def c30(k, r, o, a):
        if (k, r) not in lists:
            return None
        ix, oo = lists[(k, r)]
        lo = np.searchsorted(oo, o - W30, "left"); hi = np.searchsorted(oo, o, "left")
        sel = ix[lo:hi]; sel = sel[(spk[sel] != a) & (spk[sel] != planted)]
        if not len(sel):
            return None
        c = V[sel].sum(0); nn = np.linalg.norm(c)
        return c / nn if nn > 0 else None

    for passno in (0, 1):
        for q in range(n):
            a = int(spk[q])
            if (a == planted) != (passno == 1):
                continue
            k = int(di[q]); r = int(room[q])
            kk = other_day[k] if a == planted else k
            v = fields[(kk, r)][mi[q]] + style.get(a, 0) + noise[q]
            if a >= 0:
                c = c30(kk, r, off[q], a)
                if c is not None:
                    v = v + alpha * c
            V[q] = v / np.linalg.norm(v)
    return V


def run_synth(n_rep=10, noise_sd=1.0):
    chat = chat_full(); tl = room_lookup()
    res = {"noise_sd": noise_sd}
    for g in (38, 51):
        days = period_days_any(g)
        if g == 51:
            days = days[:15]
        C = chat.filter(pl.col("pt_date").is_in(days) & pl.col("erow").is_not_null()).sort("t")
        top = C.filter(pl.col("speaker_kind").cast(pl.Utf8) == "agent").group_by("agent").len().sort("len", descending=True)
        planted = int(top["agent"][len(top) // 2])
        reps = []
        for r in range(n_rep):
            rng = np.random.default_rng(100 * g + r)
            V = synth_vectors_monitor(days, C, rng, planted, noise_sd=noise_sd)
            F = monitor_frame(g, C, tl, None, V=V, days=days)
            D = flag_days(F, r)
            pl_ = D.filter((pl.col("agent") == planted) & pl.col("flag").is_not_null())
            rest = summarize_flags(D.filter(pl.col("agent") != planted), exclude_cc=False)
            reps.append({"planted_flag_share": float(pl_["flag"].mean()) if pl_.height else None,
                         "coupled_flagged": rest["flagged_share"], "coupled_floor": rest["floor_share"],
                         "coupled_excess_pp": rest["excess_pp"], "coupled_median_M": rest["median_M"],
                         "planted_median_M": float(pl_["M"].median()) if pl_.height else None,
                         "coupled_max_run": rest["max_consecutive_flagged_days"]})
            print(gname(g), r, reps[-1], flush=True)
        res[gname(g)] = {"planted_agent": planted, "reps": reps,
                         "planted_flag_share_mean": float(np.mean([x["planted_flag_share"] for x in reps if x["planted_flag_share"] is not None])),
                         "coupled_excess_pp_mean": float(np.mean([x["coupled_excess_pp"] for x in reps]))}
    jdump(res, OUT2 / f"r5_synthetic_noise{noise_sd:g}.json")


# ----------------------------------------------------------------------------- real
def run_real():
    OUT2.mkdir(parents=True, exist_ok=True)
    out = {"fetch_audit": fetch_audit(), "status_audit": status_audit()}
    fa = out["fetch_audit"]
    print("episodes", fa["episodes"]); print("replay span", fa["replay_span"], "pre", fa["pre_span"]); print("monitor", fa.get("monitor"))
    sa = out["status_audit"]
    print("status pre", {k: v for k, v in sa["pre"].items()}); print("status replay", sa["replay_span"])
    chat = chat_full(); tl = room_lookup()
    Es = {k: np.load(SH / "embeddings" / v, mmap_mode="r") for k, v in MODELS.items()}
    mon = {}
    for g in sorted(PERIODS):
        mon[gname(g)] = {}
        for k, E in Es.items():
            F = monitor_frame(g, chat, tl, E)
            if F is None or not F.height:
                continue
            D = flag_days(F, g)
            D.write_parquet(OUT2 / f"monitor_{gname(g)}_{k}.parquet", compression="zstd")
            mon[gname(g)][k] = {"standard": summarize_flags(D)}
            ccd = D.filter((pl.col("agent") == CC_AGENT))
            if ccd.height:
                mon[gname(g)][k]["cc_days"] = ccd.to_dicts()
        s = mon[gname(g)].get("bge", {}).get("standard")
        print(gname(g), "bge", s, flush=True)
    # Claude Code agent: M on replay-span days vs current-feed days
    ccres = {}
    for k in MODELS:
        rows = [r for gg in mon.values() for r in gg.get(k, {}).get("cc_days", [])]
        if not rows:
            continue
        cur = [r for r in rows if r["pt_date"] < REPLAY_START]; rep = [r for r in rows if r["pt_date"] >= REPLAY_START]
        wm = lambda L: float(np.sum([r["M"] * r["n"] for r in L]) / max(np.sum([r["n"] for r in L]), 1)) if L else None
        ccres[k] = {"M_current": wm(cur), "M_replay": wm(rep), "n_current": int(sum(r["n"] for r in cur)),
                    "n_replay": int(sum(r["n"] for r in rep)), "days_current": len(cur), "days_replay": len(rep),
                    "flagged_current": sum(bool(r["flag"]) for r in cur if r["flag"] is not None),
                    "flagged_replay": sum(bool(r["flag"]) for r in rep if r["flag"] is not None)}
        if ccres[k]["M_current"] and ccres[k]["M_replay"] is not None:
            ccres[k]["ratio"] = ccres[k]["M_replay"] / ccres[k]["M_current"]
    out["cc_monitor"] = ccres
    print("CC monitor", ccres)
    out["monitor"] = mon
    # R5-c: ledger omitted share
    om = {}
    for g in sorted(PERIODS):
        days = period_days_any(g)
        cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout"))
              .select("turn_id").collect())
        it = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("turn_id").is_in(cw["turn_id"].implode())
                                                                          & (pl.col("kind").cast(pl.Utf8) == "agent"))
              .select("omitted").collect())
        om[gname(g)] = {"n_items": it.height, "omitted_share": float(it["omitted"].mean()) if it.height else None}
    out["omitted"] = om
    print("omitted", om)
    jdump(out, OUT2 / "r5_audit.json")
    write_provenance("r2 R5 (r2/r5_audit.json, cc_fetch_audit, monitor_*)", "hypotheses/H08-context-is-the-coupling/analysis/r5_exposure_audit.py",
                     ["cc/cc_fetches", "cc/cc_seen", "cc/cc_village_events", "r2/cc_status", "chat_core", "embeddings/chat_*",
                      "rooms_timeline", "call_windows", "context_ledger_items", "calendar"],
                     {"stale_s": STALE_S, "episode_min_fetches": 3, "monitor_window_min": 30, "flag": "n>=10 and lo95<=0"},
                     folder=OUT2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["synth", "real"])
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--noise", type=float, default=1.0)
    a = ap.parse_args()
    run_synth(a.reps, a.noise) if a.mode == "synth" else run_real()


if __name__ == "__main__":
    main()
