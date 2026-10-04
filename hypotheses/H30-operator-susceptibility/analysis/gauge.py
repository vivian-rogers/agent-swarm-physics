"""chi_op: an operator-susceptibility gauge for any LLM-agent swarm, computed from plain logs.

    from gauge import chi_op
    report = chi_op(actions, op_msgs, statements=None, windows=None)
    report["daily"]      # one row per day x message class: n, chi_act (+se), chi_con (+se)
    report["period"]     # period estimates with day-block bootstrap CIs
    report["stability"]  # is the day-to-day variation more than sampling noise? (permutation test, reliability, lag-1)

Inputs (polars DataFrames; timestamps are UTC datetimes):
  actions     agent, t                     every agent action or event (tool call, message, ...); optional bool column
                                           `paused` marks declared idle/pause rows
  op_msgs     msg, t, kind, targets, recipients
                                           kind: "nudge" (automated / operator prompt) or "human"; targets: list of agents
                                           the message names; recipients: list of agents who can see it (e.g. the room)
              optional `vec`               message embedding (list[float]) for the content channel
  statements  agent, t, vec                optional: the agents' own messages / plans, embedded with the same model
  windows     day, start, end              optional: the swarm's active window per day (default: first/last action)

What it computes (definitions as in hypotheses/H30-operator-susceptibility/README.md, Amendments A1 and A2):
  chi_act  extra active minutes of a recipient in the 30 min after one message, from a local projection with
           matched pre-history strata (agent x state x recent activity x idle duration x time since last directed
           message x time of day) plus a day fixed effect; past messages adjusted, future *undirected* messages adjusted,
           future directed messages deliberately NOT adjusted (they depend on the agent's response). For nudges this is
           the effect of nudging now relative to the nudger's default policy.
  chi_con  movement of the recipient's next statements toward the part of the message that is NOT already in its
           own recent statements (orthogonalized), relative to same-kind messages from other days. Needs embeddings.
Classes: N_tgt (nudge naming the agent), N_by (nudge seen by others), H_men (human message naming the agent),
         H_und (human message in the agent's room). Use at 1-min resolution; at least ~100 kicks per window for a
         usable activity estimate (see the H30 card for why a single day is rarely enough).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h30lib import (CLASSES, Panel, boot_mean_by_day, boot_weights, build_base, content_scores, daily_activity,  # noqa: E402
                    daily_mean, fit_activity, kick_columns, np, period_ci, pl, pre_post_means, stability, unit,
                    window_reliability)


def _windows(actions: pl.DataFrame, windows: pl.DataFrame | None) -> pl.DataFrame:
    if windows is not None:
        return windows.sort("start")
    return (actions.with_columns(pl.col("t").dt.date().cast(pl.Utf8).alias("day"))
            .group_by("day").agg(pl.col("t").min().alias("start"), pl.col("t").max().alias("end")).sort("start"))


def build_panels(actions: pl.DataFrame, windows: pl.DataFrame) -> list[Panel]:
    panels = []
    has_pause = "paused" in actions.columns
    for k, (day, start, end) in enumerate(windows.select("day", "start", "end").iter_rows()):
        a = actions.filter((pl.col("t") >= start) & (pl.col("t") <= end))
        if a.height == 0:
            continue
        nm = int((end - start).total_seconds() // 60) + 1
        agents = np.array(sorted(a["agent"].unique().to_list()), dtype=object)
        amap = {x: i for i, x in enumerate(agents)}
        act = np.zeros((len(agents), nm), np.int8); idle = np.zeros((len(agents), nm), np.int8)
        mins = ((a["t"] - start).dt.total_seconds() // 60).cast(pl.Int64).to_numpy()
        rows = np.array([amap[x] for x in a["agent"].to_list()])
        pz = a["paused"].to_numpy() if has_pause else np.zeros(a.height, bool)
        act[rows[~pz], mins[~pz]] = 1
        idle[rows[pz], mins[pz]] = 1
        codes = np.arange(len(agents))  # integer codes for strata; mapping kept in panel label
        p = Panel(day=k, act=act, idle=idle, agents=codes, label=str(day), goal_day=k)
        p.names = agents
        panels.append(p)
    return panels


def build_kicks(panels: list[Panel], windows: pl.DataFrame, op_msgs: pl.DataFrame) -> pl.DataFrame:
    rows = []
    wmap = {str(d): s for d, s in windows.select("day", "start").iter_rows()}
    for mi, (msg, t, kind, targets, recips) in enumerate(op_msgs.select("msg", "t", "kind", "targets", "recipients").iter_rows()):
        for p in panels:
            s = wmap[p.label]
            minute = int((t - s).total_seconds() // 60)
            if 0 <= minute < p.n_min:
                names = {x: i for i, x in enumerate(p.names)}
                tg = set(targets or []); rec = set(recips or []) | (tg if kind == "nudge" else set())
                for a in rec:
                    if a not in names:
                        continue
                    if kind == "nudge":
                        cls = "N_tgt" if a in tg else "N_by"
                    else:
                        cls = "H_men" if a in tg else "H_und"
                    rows.append((p.day, names[a], names[a], minute, cls, mi, kind, t.timestamp(), a))
                break
    return pl.DataFrame(rows, schema={"day": pl.Int32, "row": pl.Int32, "agent": pl.Int32, "minute": pl.Int32, "cls": pl.Utf8,
                                      "msg": pl.Int64, "kind": pl.Utf8, "ts": pl.Float64, "agent_name": pl.Object}, orient="row")


def _whitener(V: np.ndarray, dim: int = 32):
    mu = V.mean(0)
    w, U = np.linalg.eigh(np.cov((V - mu).T))
    o = np.argsort(w)[::-1][:dim]
    U, w = U[:, o], w[o]
    return lambda X: ((np.asarray(X, np.float32) - mu) @ U) / np.sqrt(w)


def chi_op(actions: pl.DataFrame, op_msgs: pl.DataFrame, statements: pl.DataFrame | None = None,
           windows: pl.DataFrame | None = None, n_boot: int = 1000, dim: int = 32) -> dict:
    win = _windows(actions, windows)
    panels = build_panels(actions, win)
    kicks = build_kicks(panels, win, op_msgs)
    base = build_base(panels, kicks=kicks)
    X = kick_columns(base, kicks)
    fit = fit_activity(base, X)
    W = boot_weights(len(panels), n_boot)
    period = {"act": {c: v for c, v in period_ci(fit, W).items()}}
    daily = daily_activity(fit).rename({"chi": "chi_act", "se": "se_act"})
    kv = fit.kick_r.join(kicks.unique(["day", "row", "minute", "cls"]).select("day", "row", "minute", "cls", pl.col("msg").alias("cluster")),
                         on=["day", "row", "minute", "cls"], how="left")
    stab = {}
    for c in CLASSES:
        d = daily.filter(pl.col("cls") == c).select("day", "n", pl.col("chi_act").alias("chi"), pl.col("se_act").alias("se"))
        st = stability(d, kick_values=kv.filter(pl.col("cls") == c))
        if st.get("n_days_eligible", 0) >= 4:
            st["windows"] = [window_reliability(d, w) for w in (3, 5, 10)]
        stab[f"act_{c}"] = st
    if statements is not None and "vec" in op_msgs.columns:
        V = np.array(statements["vec"].to_list(), np.float32)
        Wh = _whitener(V, dim)
        sv = unit(Wh(V)).astype(np.float32)
        names = {}
        for p in panels:
            for i, a in enumerate(p.names):
                names.setdefault(a, None)
        st_t, st_v = {}, {}
        ts = np.array([t.timestamp() for t in statements["t"].to_list()])
        ag = statements["agent"].to_list()
        # agent codes in kicks are per-day rows; content uses agent names -> map to a stable int
        amap = {a: i for i, a in enumerate(sorted(set(ag) | set(kicks["agent_name"].to_list())))}
        agi = np.array([amap[a] for a in ag])
        for a in np.unique(agi):
            m = agi == a
            o = np.argsort(ts[m])
            st_t[int(a)] = ts[m][o]; st_v[int(a)] = sv[m][o]
        U = unit(Wh(np.array(op_msgs["vec"].to_list(), np.float32))).astype(np.float32)
        pairs = (kicks.with_columns(pl.Series("agent", [amap[a] for a in kicks["agent_name"].to_list()], dtype=pl.Int64))
                 .with_row_index("pair").with_columns(pl.col("pair").cast(pl.Int64)))
        mm = pl.DataFrame({"msg": np.arange(op_msgs.height), "day": [None] * op_msgs.height,
                           "kind": op_msgs["kind"].to_list(),
                           "targets": [[amap.get(x, -1) for x in (t or [])] for t in op_msgs["targets"].to_list()]})
        dmap = kicks.group_by("msg").agg(pl.col("day").first())
        mm = mm.drop("day").join(dmap.with_columns(pl.col("msg").cast(pl.Int64)), on="msg", how="left").with_columns(
            pl.col("day").fill_null(-1))
        P, Q, npre, npost, S = pre_post_means(st_t, st_v, pairs)
        cs = content_scores(pairs.select("pair", "msg", "agent", "day", "cls", "kind"), P, Q, U, mm, S=S)
        dc = daily_mean(cs.filter(pl.col("chi_orth").is_not_nan()), "chi_orth").rename({"chi": "chi_con", "se": "se_con", "n": "n_con"})
        daily = daily.join(dc, on=["day", "cls"], how="full", coalesce=True)
        period["con"] = {c: boot_mean_by_day(cs.filter((pl.col("cls") == c) & pl.col("chi_orth").is_not_nan()), "chi_orth",
                                             np.arange(len(panels)), W) for c in CLASSES}
        for c in CLASSES:
            sub = cs.filter((pl.col("cls") == c) & pl.col("chi_orth").is_not_nan())
            d = daily_mean(sub, "chi_orth")
            stab[f"con_{c}"] = stability(d, kick_values=sub.select("day", "agent", pl.col("msg").alias("cluster"),
                                                                    pl.col("chi_orth").alias("r")), weight_col=None)
    labels = {p.day: p.label for p in panels}
    daily = daily.with_columns(pl.col("day").replace_strict(labels, default=None).alias("date")).sort("day", "cls")
    return {"daily": daily, "period": period, "stability": stab, "n_days": len(panels), "n_kicks": fit.n_kicks}


if __name__ == "__main__":
    # Self-test on a simulated swarm (H30 synthetic generator), converted to the plain-log format.
    import datetime as dt
    from synthetic import simulate
    panels, kicks, mm, U, st_t, st_v, par = simulate("G38like", "S1_const", 7)
    t0 = dt.datetime(2026, 1, 5, 17, 0, tzinfo=dt.timezone.utc)
    acts, wins = [], []
    for p in panels:
        start = t0 + dt.timedelta(days=p.day)
        wins.append((p.label, start, start + dt.timedelta(minutes=p.n_min - 1)))
        r, m = np.nonzero(p.act)
        acts += [(f"a{int(p.agents[i])}", start + dt.timedelta(minutes=int(mi), seconds=10), False) for i, mi in zip(r, m)]
        r, m = np.nonzero(p.idle)
        acts += [(f"a{int(p.agents[i])}", start + dt.timedelta(minutes=int(mi), seconds=10), True) for i, mi in zip(r, m)]
    actions = pl.DataFrame(acts, schema=["agent", "t", "paused"], orient="row")
    windows = pl.DataFrame(wins, schema=["day", "start", "end"], orient="row")
    msg_rows = []
    km = kicks.group_by("msg").agg(pl.col("day").first(), pl.col("minute").first(), pl.col("kind").first(),
                                   pl.col("agent").filter(pl.col("cls").is_in(["N_tgt", "H_men"])).alias("tg"),
                                   pl.col("agent").alias("rec"))
    for msg, day, minute, kind, tg, rec in km.sort("msg").iter_rows():
        msg_rows.append((msg, t0 + dt.timedelta(days=day, minutes=minute, seconds=30), kind, [f"a{x}" for x in tg],
                         [f"a{x}" for x in rec], U[msg].tolist()))
    op = pl.DataFrame(msg_rows, schema=["msg", "t", "kind", "targets", "recipients", "vec"], orient="row")
    srows = []
    for a, ts in st_t.items():
        for tt, v in zip(ts, st_v[a]):
            day = int(tt // 86400); sec = tt - day * 86400
            srows.append((f"a{a}", t0 + dt.timedelta(days=day, seconds=sec), v.tolist()))
    stm = pl.DataFrame(srows, schema=["agent", "t", "vec"], orient="row")
    rep = chi_op(actions, op, statements=stm, windows=windows, n_boot=200)
    truth = kicks.group_by("cls").agg(pl.col("e_act").mean(), pl.col("e_con").mean())
    print("period activity:", {k: v for k, v in rep["period"]["act"].items() if k in CLASSES})
    print("period content:", rep["period"].get("con"))
    print("truth:", truth.sort("cls").to_dicts())
    print(rep["daily"].head(8))
