"""H58 re-acquisition path after member erasures (card F9; predictions P6, P7). Regime III units only.

For each forced erasure (NE41), voluntary consolidation and placebo call (mid-segment, ctx_pos 20, no reset in the next
10 calls) of an agent whose multi-layer community (card F7) has >= 2 members:
  k_pre  the agent's last committed repo in the 60 min before;  k_G  the other members' dominant repo in the 60 min before
  outcome (first commit within the 10-call window, <= 30 min): own (k_pre), group (k_G != k_pre), other, none
  sources before that commit: the consolidation intention names k_pre / k_G (memory/prompt-held); an executed command
  reads k_pre / k_G (artifact-held); a new chat item from a community member, or one naming k_pre / k_G (peer-held)
P6: erasure vs placebo P(group) among divergent events (k_pre != k_G), Mantel-Haenszel by agent.
P7: the member's and the other members' commits on R_G in the 15 min after, erasure vs placebo (agent-day clusters).
Output: data/processed/H58-coordinated-superagents/results/reacq.json (+ reacq_events.parquet, codes only).
Run: uv run python hypotheses/H58-coordinated-superagents/analysis/reacq.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ[_v] = "2"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h58data as HD  # noqa: E402
import h58lib as L  # noqa: E402
from run import jsonable  # noqa: E402

OUT = HD.D / "results"


def unit_context(name):
    """Multi-layer communities (agent codes) and each community's R_G (global repo ids) for one unit."""
    U = HD.load_unit(name)
    M = L.layer_matrices(list(U.agents), HD.layer_rows(name))
    comms = L.communities(M["multi"]) if M["multi"].sum() > 0 else []
    out = {}
    for c in comms:
        R = [int(U.repos[k]) for k in U.shared_artifacts(c)]
        ag = [int(U.agents[a]) for a in c]
        for a in ag:
            out[a] = {"members": ag, "R": R}
    return out


def dominant(rows):
    if not rows:
        return None
    v, c = np.unique(np.asarray(rows), return_counts=True)
    return int(v[c.argmax()])


def next_resets(meta):
    """Per (unit, day, agent): sorted minutes (since the window start) of the agent's resets (context ledger)."""
    import datetime as dt
    days = []
    for x in meta:
        if x["regime"] != "III":
            continue
        for d, (day, ws) in enumerate(zip(x["days"], x["win_start"])):
            days.append((x["unit"], d, day, dt.datetime.fromisoformat(ws)))
    D = pl.DataFrame(days, schema=["unit", "day", "pt_date", "win_start"], orient="row")
    tu = pl.scan_parquet(HD.SH / "context_ledger_turns.parquet").filter(
        ~pl.col("holdout") & (pl.col("reset_consol") | pl.col("reset_session"))
        & pl.col("pt_date").is_in(D["pt_date"].to_list())).select("agent", "pt_date", "t_call").collect()
    tu = tu.join(D, on="pt_date").with_columns(
        ((pl.col("t_call") - pl.col("win_start")).dt.total_microseconds() / 6e7).alias("m"))
    out = {}
    for (u, d, a), g in tu.partition_by(["unit", "day", "agent"], as_dict=True).items():
        out[(u, d, a)] = np.sort(g["m"].to_numpy())
    return out


def collect_events(meta, E):
    """Per-event table (codes only) for the regime-III units in meta."""
    NR = next_resets(meta)
    C = pl.read_parquet(HD.D / "commits.parquet").select("unit", "day", "m", "agent", "repo_id")
    rows = []
    for x in meta:
        if x["regime"] != "III":
            continue
        u = x["unit"]
        ctx = unit_context(u)
        cu = C.filter(pl.col("unit") == u)
        cday = {d: g.sort("m") for (d,), g in cu.partition_by("day", as_dict=True).items()}
        eu = E.filter(pl.col("unit") == u)
        for r in eu.iter_rows(named=True):
            a = r["agent"]
            if a not in ctx:
                continue
            mem, R = ctx[a]["members"], ctx[a]["R"]
            others = [b for b in mem if b != a]
            cd = cday.get(r["day"])
            if cd is None:
                continue
            m = r["m"]
            pre = cd.filter((pl.col("m") >= m - 60) & (pl.col("m") < m))
            k_G = dominant(pre.filter(pl.col("agent").is_in(others))["repo_id"].to_list())
            k_pre = r["k_pre"]
            # outcome window: until the agent's next reset (or 30 min); the 10-call version is kept as a variant
            nr = NR.get((u, r["day"], a), np.array([]))
            nxt = nr[nr > m + 0.05]
            t_end = min(m + 30, nxt[0]) if len(nxt) else m + 30
            fc = cd.filter((pl.col("agent") == a) & (pl.col("m") >= m) & (pl.col("m") < t_end))
            k_seg = int(fc["repo_id"][0]) if fc.height else None
            k10 = r["k10"]

            def cls(k):
                if k is None:
                    return "none"
                if k_pre is not None and k == k_pre:
                    return "own"
                if k_G is not None and k == k_G:
                    return "group"
                return "other"
            outc_seg = cls(k_seg)
            if k10 is None:
                outc = "none"
            elif k_pre is not None and k10 == k_pre:
                outc = "own"
            elif k_G is not None and k10 == k_G:
                outc = "group"
            else:
                outc = "other"
            post = cd.filter((pl.col("m") >= m) & (pl.col("m") < m + 15))
            pre15 = cd.filter((pl.col("m") >= m - 15) & (pl.col("m") < m))
            senders = set(int(s) for s in (r["peer_senders"] or []) if s is not None and s >= 0)
            named = set(r["peer_named"] or [])
            reads = set(r["reads"] or [])
            intent = set(r["intent_repos"] or [])
            rows.append({
                "unit": u, "agent": a, "day": r["day"], "m": m, "etype": r["etype"], "k_pre": k_pre, "k_G": k_G,
                "divergent": bool(k_pre is not None and k_G is not None and k_pre != k_G), "outcome": outc_seg,
                "outcome10": outc, "seg_min": t_end - m,
                "t10": r["t10"], "n_members": len(mem),
                "int_pre": bool(k_pre is not None and k_pre in intent), "int_G": bool(k_G is not None and k_G in intent),
                "int_any": bool(intent),
                "read_pre": bool(k_pre is not None and k_pre in reads), "read_G": bool(k_G is not None and k_G in reads),
                "read_any": bool(reads),
                "peer_member": bool(senders & set(others)), "peer_named_pre": bool(k_pre is not None and k_pre in named),
                "peer_named_G": bool(k_G is not None and k_G in named),
                "self_post15": int(post.filter(pl.col("agent") == a).height),
                "self_pre15": int(pre15.filter(pl.col("agent") == a).height),
                "others_post15_R": int(post.filter(pl.col("agent").is_in(others) & pl.col("repo_id").is_in(R)).height),
                "others_pre15_R": int(pre15.filter(pl.col("agent").is_in(others) & pl.col("repo_id").is_in(R)).height),
            })
    return pl.DataFrame(rows, infer_schema_length=None)


def statistics(ev, meta):
    res = {"n_events": ev.group_by("etype").agg(pl.len()).rows()}
    # ---- outcome shares by event type (all events with k_pre; and divergent ones)
    def shares(df):
        n = df.height
        return {o: (df.filter(pl.col("outcome") == o).height / n if n else None) for o in ("own", "group", "other", "none")} | {"n": n}
    res["outcomes_kpre"] = {et: shares(ev.filter((pl.col("etype") == et) & pl.col("k_pre").is_not_null()))
                            for et in ("forced", "voluntary", "placebo")}
    res["outcomes_divergent"] = {et: shares(ev.filter((pl.col("etype") == et) & pl.col("divergent")))
                                 for et in ("forced", "voluntary", "placebo")}
    # ---- P6: MH log-OR of P(group) and P(own), erasure vs placebo, stratified by agent (divergent events)
    for et in ("forced", "voluntary"):
        for outc in ("group", "own", "none"):
            tabs = []
            d = ev.filter(pl.col("divergent") & pl.col("etype").is_in([et, "placebo"]))
            for (a,), g in d.partition_by("agent", as_dict=True).items():
                e1 = g.filter(pl.col("etype") == et)
                e0 = g.filter(pl.col("etype") == "placebo")
                if e1.height == 0 or e0.height == 0:
                    continue
                aa = e1.filter(pl.col("outcome") == outc).height
                cc = e0.filter(pl.col("outcome") == outc).height
                tabs.append([[aa, e1.height - aa], [cc, e0.height - cc]])
            res[f"P6_{et}_{outc}"] = L.mh_logor(tabs) | {"n_strata": len(tabs)}
        # primary (amendment A1): conditional on a commit in the window (windows differ in length: an erasure opens
        # a ~41-call segment, a placebo sits mid-segment), P(group) and P(own), erasure vs placebo
        for outc in ("group", "own"):
            tabs = []
            d = ev.filter(pl.col("divergent") & pl.col("etype").is_in([et, "placebo"]) & (pl.col("outcome") != "none"))
            for (a,), g in d.partition_by("agent", as_dict=True).items():
                e1 = g.filter(pl.col("etype") == et)
                e0 = g.filter(pl.col("etype") == "placebo")
                if e1.height == 0 or e0.height == 0:
                    continue
                aa = e1.filter(pl.col("outcome") == outc).height
                cc = e0.filter(pl.col("outcome") == outc).height
                tabs.append([[aa, e1.height - aa], [cc, e0.height - cc]])
            res[f"P6c_{et}_{outc}"] = L.mh_logor(tabs) | {"n_strata": len(tabs),
                                                          "n_events": int(sum(t[0][0] + t[0][1] for t in tabs)),
                                                          "n_placebo": int(sum(t[1][0] + t[1][1] for t in tabs))}
    # ---- sources: shares among forced / placebo events with k_pre, and among returns to own
    def src(df):
        n = df.height
        out = {"n": n}
        for c in ("int_pre", "int_G", "int_any", "read_pre", "read_G", "read_any", "peer_member", "peer_named_pre",
                  "peer_named_G"):
            out[c] = df[c].mean() if n else None
        if n:
            out["none_of_three_pre"] = float((~df["int_pre"] & ~df["read_pre"] & ~df["peer_named_pre"]).mean())
        return out
    res["sources"] = {}
    for et in ("forced", "voluntary", "placebo"):
        d = ev.filter((pl.col("etype") == et) & pl.col("k_pre").is_not_null())
        res["sources"][et] = {"all": src(d), "returned_own": src(d.filter(pl.col("outcome") == "own")),
                              "went_group": src(d.filter(pl.col("outcome") == "group"))}
    # return to own conditional on sources (forced events with k_pre and a commit in the window)
    d = ev.filter((pl.col("etype") == "forced") & pl.col("k_pre").is_not_null() & (pl.col("outcome") != "none"))
    res["own_given_source"] = {}
    for c in ("int_pre", "read_pre", "peer_named_pre", "peer_member"):
        a1 = d.filter(pl.col(c))
        a0 = d.filter(~pl.col(c))
        res["own_given_source"][c] = {"with": (a1.filter(pl.col("outcome") == "own").height / a1.height) if a1.height else None,
                                      "n_with": a1.height,
                                      "without": (a0.filter(pl.col("outcome") == "own").height / a0.height) if a0.height else None,
                                      "n_without": a0.height}
    # ---- P7: member and others' commits in the 15 min after, erasure vs placebo (agent-day cluster bootstrap)
    rng = np.random.default_rng(58)
    for et in ("forced", "voluntary"):
        d = ev.filter(pl.col("etype").is_in([et, "placebo"]))
        d = d.with_columns((pl.col("agent").cast(pl.Utf8) + "|" + pl.col("unit") + "|" + pl.col("day").cast(pl.Utf8)).alias("cl"))
        def diff(dd):
            e1, e0 = dd.filter(pl.col("etype") == et), dd.filter(pl.col("etype") == "placebo")
            if e1.height == 0 or e0.height == 0:
                return np.nan, np.nan
            return (e1["self_post15"].mean() - e0["self_post15"].mean(),
                    e1["others_post15_R"].mean() - e0["others_post15_R"].mean())
        ds, do = diff(d)
        cls = d["cl"].unique().to_list()
        parts = {c: g for (c,), g in d.partition_by("cl", as_dict=True).items()}
        bs = []
        for _ in range(300):
            pick = rng.choice(len(cls), len(cls))
            bs.append(diff(pl.concat([parts[cls[i]] for i in pick])))
        bs = np.asarray(bs, float)
        base_self = d.filter(pl.col("etype") == "placebo")["self_post15"].mean()
        base_oth = d.filter(pl.col("etype") == "placebo")["others_post15_R"].mean()
        beta = (ds + do) / ds if ds and np.isfinite(ds) and abs(ds) > 1e-9 else np.nan
        bb = (bs[:, 0] + bs[:, 1]) / bs[:, 0]
        res[f"P7_{et}"] = {"d_self": ds, "d_self_se": float(np.nanstd(bs[:, 0])), "d_others": do,
                           "d_others_se": float(np.nanstd(bs[:, 1])),
                           "z_others": do / float(np.nanstd(bs[:, 1])) if np.nanstd(bs[:, 1]) > 0 else np.nan,
                           "base_self": base_self, "base_others": base_oth, "rel_self": ds / base_self if base_self else np.nan,
                           "rel_others": do / base_oth if base_oth else np.nan, "beta": beta,
                           "beta_ci": [float(np.nanpercentile(bb, 2.5)), float(np.nanpercentile(bb, 97.5))],
                           "n_events": d.filter(pl.col("etype") == et).height,
                           "n_placebo": d.filter(pl.col("etype") == "placebo").height}
    # per-unit outcome shares (forced, divergent) for period folders
    res["per_unit"] = {}
    for x in meta:
        if x["regime"] != "III":
            continue
        u = x["unit"]
        du = ev.filter(pl.col("unit") == u)
        res["per_unit"][u] = {"forced_div": shares(du.filter((pl.col("etype") == "forced") & pl.col("divergent"))),
                              "placebo_div": shares(du.filter((pl.col("etype") == "placebo") & pl.col("divergent"))),
                              "forced_kpre": shares(du.filter((pl.col("etype") == "forced") & pl.col("k_pre").is_not_null()))}
    return res


def main():
    meta = HD.units_meta()
    HD.assert_no_holdout(meta)
    E = pl.read_parquet(HD.D / "erasures.parquet")
    ev = collect_events(meta, E)
    ev.write_parquet(OUT / "reacq_events.parquet", compression="zstd")
    res = statistics(ev, meta)
    (OUT / "reacq.json").write_text(json.dumps(jsonable(res), indent=1))
    print(json.dumps(jsonable({k: v for k, v in res.items() if k != "per_unit"}), indent=1)[:6000])


if __name__ == "__main__":
    main()
