"""H07 round 1b (2026-10-04): re-checks on corrected shared inputs, plus three natives. Exploratory, non-holdout only.

Runs only with H07_DATA=r1b (round-1 scripts unchanged). Outputs: data/processed/H07-rpg-forks/r1b/results_r1b.json.
Parts:
  copyinfo  end-of-#35 vertical and horizontal decompositions with shared infra/shared/copy_info.py vs h07lib
  dq4       fork commits matched to the DQ4 work ledger (automated / non-agent flags); P6 on agent work
  p8        P8 re-scored on DQ6 room_assignment (#35)
  ledger    NE15 native: cross-team chat items read (context ledger) by team, period and day; shared innovations
            checked for a cross-team read naming the item before the later commit (text matched in memory only);
            cross-fork commit authors' prior reads of the other fork's repo/site
  lead      G35 native: keyed content changes (names + data numbers) attributed to first-parent commits vs the DQ6
            lead designer of the room-day
  papers    G36 native: the agent-papers fork family (file features: path -> blob id, trees only)
Usage: H07_DATA=r1b uv run python hypotheses/H07-rpg-forks/analysis/round1b.py [part ...]
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ[_v] = "2"

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h07lib as L  # noqa: E402
from h07lib import P, ROOT, SH, T0, T35_END, UTC  # noqa: E402

sys.path.insert(0, str(ROOT / "infra/shared"))
import copy_info as CI  # noqa: E402
from common import holdout_mask  # noqa: E402

R1B = P / "r1b"
OUTF = R1B / "results_r1b.json"
END37 = dt.datetime(2026, 4, 2, 7, 0, tzinfo=UTC)
REPOS = {"best": "github.com/ai-village-agents/rpg-game-best", "rest": "github.com/ai-village-agents/rpg-game-rest"}
SITES = {"best": "ai-village-agents.github.io/rpg-game-best", "rest": "ai-village-agents.github.io/rpg-game-rest"}


def teams35():
    g = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        pl.col("preferred") & ~pl.col("holdout") & (pl.col("goal_no") == 35) & (pl.col("label_kind") == "room_assignment"))
    return dict(zip(g["agent"].to_list(), g["value"].to_list()))


def part_copyinfo():
    snaps, trees = L.load_trees()
    feats = L.Features()
    A = snaps.filter(pl.col("lineage") == "ancestor")["sha"][0]
    KA, _ = feats.of_tree(trees[A])
    ds = pl.read_parquet(P / "day_snapshots.parquet")
    end = {lin: ds.filter((pl.col("lineage") == lin) & (pl.col("pt_date") <= "2026-03-20")).sort("pt_date")["sha"][-1]
           for lin in ("best", "rest")}
    K = {lin: feats.of_tree(trees[s])[0] for lin, s in end.items()}
    out, maxdiff = {}, 0.0
    for f in L.FEATURES:
        for lin in ("best", "rest"):
            a, b = L.vertical(KA[f], K[lin][f]), CI.vertical(KA[f], K[lin][f])
            out[f"{lin}/{f}"] = {m: b[m] for m in ("c", "kappa", "I", "I_copy")}
            maxdiff = max(maxdiff, *(abs(a[m] - b[m]) for m in ("c", "kappa", "I", "I_copy")))
        a, b = L.horizontal(K["best"][f], K["rest"][f]), CI.horizontal(K["best"][f], K["rest"][f])
        out[f"horizontal/{f}"] = {m: b[m] for m in ("c", "kappa", "I", "I_copy")}
        maxdiff = max(maxdiff, *(abs(a[m] - b[m]) for m in ("c", "kappa", "I", "I_copy")))
    return {"end_sha": end, "values": out, "max_abs_diff_vs_h07lib": maxdiff}


def part_dq4():
    cm = pl.read_parquet(P / "commits.parquet").filter(pl.col("lineage").is_in(["best", "rest"]) & ~pl.col("is_merge"))
    wc = pl.scan_parquet(SH / "work_commits.parquet").filter(pl.col("repo").cast(pl.String).is_in(list(REPOS.values()))).select(
        pl.col("repo").cast(pl.String), pl.col("hash").alias("sha"), "automated", pl.col("author_kind").cast(pl.String),
        "canonical", "imported", "author_agent").collect().unique("sha")
    j = cm.join(wc, on="sha", how="left")
    j = j.with_columns((pl.col("canonical").fill_null(False) & ~pl.col("imported").fill_null(False)
                        & (pl.col("author_kind") == "agent") & ~pl.col("automated").fill_null(True)).alias("agent_work"))
    out = {"n_commits": cm.height, "matched": int(j["automated"].is_not_null().sum()),
           "automated": int(j["automated"].fill_null(False).sum()), "agent_work": int(j["agent_work"].sum()),
           "author_agrees": int((j["author_agent"] == j["agent"]).fill_null(False).sum())}
    in35 = j.filter(pl.col("t_commit") <= T35_END)
    tm = teams35()
    per = {}
    for lin in ("best", "rest"):
        g = in35.filter(pl.col("lineage") == lin)
        n_agents = sum(1 for v in tm.values() if v == lin)
        per[lin] = {"commits_35": g.height, "agent_work_35": int(g["agent_work"].sum()), "team_size_dq6": n_agents,
                    "per_capita_all": g.height / n_agents, "per_capita_work": int(g["agent_work"].sum()) / n_agents}
    out["P6_35"] = per
    out["non_work"] = j.filter(~pl.col("agent_work")).select("lineage", "sha", "author", "automated", "author_kind",
                                                              "canonical", "imported").to_dicts()
    return out


def part_p8():
    tm = teams35()
    cm = pl.read_parquet(P / "commits.parquet").filter(pl.col("lineage").is_in(["best", "rest"]) & (pl.col("t_commit") >= T0))
    out = {}
    for lin in ("best", "rest"):
        for nm, g in (("all", cm), ("in35", cm.filter(pl.col("t_commit") <= T35_END))):
            g = g.filter(pl.col("lineage") == lin)
            own = sum(1 for a in g["agent"].to_list() if a is not None and tm.get(a) == lin)
            out[f"{lin}/{nm}"] = {"n": g.height, "own_team": own, "share": own / g.height if g.height else None,
                                  "unmapped": int(g["agent"].is_null().sum())}
    return out


def _reads(t_lo, t_hi):
    cw = pl.scan_parquet(SH / "call_windows.parquet").filter((pl.col("t_call") >= t_lo) & (pl.col("t_call") < t_hi)).select(
        "turn_id", "agent", "t_call", "goal_no", "pt_date").collect()
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("kind").cast(pl.String) == "agent").select(
        "turn_id", "message_id", "sender").collect()
    return it.join(cw, on="turn_id", how="inner").rename({"agent": "recipient"})


INNOV = [  # (label, regex on message text, t_first, t_second, later team) - times from round 1 shared_innovations
    ("battle-summary displayName fallback", r"battle[-_ ]?summary|displayName", "rest", "best"),
    ("tavern-dice rng fix", r"tavern[-_ ]?dice|rngValue", "best", "rest"),
    ("missing specialization abilities", r"divine[-_ ]?shield|prophecy", "rest", "best"),
]


def part_ledger():
    tm = teams35()
    held = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "holdout")
    rd = _reads(T0, END37).join(held, on="pt_date", how="left").filter(~pl.col("holdout").fill_null(False))
    rd = rd.with_columns(pl.col("recipient").replace_strict(tm, default=None, return_dtype=pl.String).alias("r_team"),
                         pl.col("sender").replace_strict(tm, default=None, return_dtype=pl.String).alias("s_team"))
    rd = rd.filter(pl.col("r_team").is_not_null() & pl.col("s_team").is_not_null())
    rd = rd.with_columns((pl.col("r_team") != pl.col("s_team")).alias("cross"))
    by_goal = rd.group_by("goal_no").agg(pl.len().alias("items"), pl.col("cross").sum().alias("cross")).sort("goal_no")
    by_day = rd.filter(pl.col("cross")).group_by("pt_date", "r_team").agg(pl.len().alias("cross_items"),
                                                                        pl.col("recipient").n_unique().alias("recipients")).sort("pt_date")
    out = {"by_goal": by_goal.with_columns((pl.col("cross") / pl.col("items")).alias("share")).to_dicts(),
           "cross_by_day": by_day.to_dicts()}
    # shared innovations: times from round 1's table (first and second commit per item)
    si = pl.read_parquet(P / "shared_innovations.parquet")
    txt = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"])
    rdt = rd.filter(pl.col("cross")).join(txt, on="message_id", how="left")
    inn = []
    for label, rx, first, later in INNOV:
        pat = {"battle-summary displayName fallback": "battle-summary", "tavern-dice rng fix": "tavern-dice",
               "missing specialization abilities": "abilities"}[label]
        rows = si.filter(pl.col("key").fill_null("").str.contains(pat) | pl.col("value").str.contains(pat))
        if label.startswith("missing"):
            rows = si.filter(pl.col("feature") == "names")
        t2 = max(max(rows["t_best"].to_list()), max(rows["t_rest"].to_list())) if rows.height else None
        t1 = min(min(rows["t_best"].to_list()), min(rows["t_rest"].to_list())) if rows.height else None
        sub = rdt.filter((pl.col("r_team") == later) & (pl.col("t_call") < t2)) if t2 else rdt.head(0)
        hit = sub.filter(pl.col("text").fill_null("").str.contains("(?i)" + rx))
        inn.append({"item": label, "t_first": t1, "t_second": t2, "later_team": later,
                    "cross_items_read_by_later_team_before": sub.height, "naming_item": hit.height,
                    "naming_before_t_first": int(hit.filter(pl.col("t_call") < t1).height) if t1 else None})
    out["innovations"] = inn
    # cross-fork commit authors: prior reads of a message naming the target fork's repo or site
    led = pl.read_parquet(P / "leakage.parquet").filter(pl.col("channel") == "commit:cross_fork")
    art = pl.read_parquet(SH / "artifacts.parquet").select("artifact", "name")
    am = pl.scan_parquet(SH / "artifact_mentions.parquet").filter(
        (pl.col("source").cast(pl.String) == "chat") & pl.col("message_id").is_not_null()).select(
        "artifact", "message_id").collect().join(art, on="artifact")
    allr = _reads(T0, dt.datetime(2026, 4, 4, tzinfo=UTC))
    cfc = []
    for t, a, target in led.select("t", "agent", "target").iter_rows():
        names = [REPOS[target], SITES[target]]
        mids = am.filter(pl.col("name").is_in(names))["message_id"].unique()
        r = allr.filter((pl.col("recipient") == a) & (pl.col("t_call") < t) & pl.col("message_id").is_in(mids))
        cfc.append({"t": t, "agent": a, "target": target, "reads_naming_target_before": r.height,
                    "first_read": r["t_call"].min() if r.height else None})
    out["cross_fork_commits"] = cfc
    return out


def part_lead():
    cc = pl.read_parquet(P / "curves_commit.parquet").sort("lineage", "k")
    cm = pl.read_parquet(P / "commits.parquet").select("lineage", "sha", "agent", "author", "is_merge")
    res = json.loads((P / "results.json").read_text())["ancestor"]
    n_names, n_num = res["n_names"], res["n_numbers_data"]
    g = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(
        pl.col("preferred") & (pl.col("goal_no") == 35) & (pl.col("label_kind") == "leader"))
    lead = {}
    for a, det, tf in g.select("agent", "detail", "t_valid_from").iter_rows():
        room = re.search(r"room=(\w+)", det).group(1)
        lead[(room, tf.date().isoformat())] = a
    out = {"lead": {f"{k[0]}/{k[1]}": v for k, v in lead.items()}}
    for lin in ("best", "rest"):
        d = cc.filter(pl.col("lineage") == lin).join(cm, on=["lineage", "sha"], how="left")
        cn = np.concatenate([[1.0], d["names_c"].to_numpy()])
        cu = np.concatenate([[1.0], d["numbers_data_c"].to_numpy()])
        steps = -np.diff(cn) * n_names - np.diff(cu) * n_num  # inherited content keys changed at each first-parent step
        d = d.with_columns(pl.Series("content", steps),
                           pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt"))
        d = d.filter(pl.col("pt").is_in(["2026-03-16", "2026-03-17", "2026-03-18"]))
        d = d.with_columns(pl.struct("pt", "agent").map_elements(lambda s: lead.get((lin, s["pt"])) == s["agent"],
                                                                  return_dtype=pl.Boolean).alias("is_lead"))
        pos = d.filter(pl.col("content") > 0)
        tot = float(pos["content"].sum())
        Lsh = float(pos.filter(pl.col("is_lead"))["content"].sum()) / tot if tot else None
        nonmerge = d.filter(~pl.col("is_merge").fill_null(False))
        Csh = float(nonmerge["is_lead"].mean()) if nonmerge.height else None
        days = []
        for pt in ("2026-03-16", "2026-03-17", "2026-03-18"):
            dd = pos.filter(pl.col("pt") == pt).sort("content", descending=True)
            if dd.height:
                days.append({"pt": pt, "top_author": dd["author"][0], "top_is_lead": bool(dd["is_lead"][0]),
                             "top_content": float(dd["content"][0]), "day_content": float(dd["content"].sum()),
                             "lead": lead.get((lin, pt))})
        # who carried the content overall (all #35 days), for the trait reading
        allc = cc.filter((pl.col("lineage") == lin) & (pl.col("t") <= T35_END)).join(cm, on=["lineage", "sha"], how="left")
        an = np.concatenate([[1.0], cc.filter(pl.col("lineage") == lin)["names_c"].to_numpy()])
        au = np.concatenate([[1.0], cc.filter(pl.col("lineage") == lin)["numbers_data_c"].to_numpy()])
        st = (-np.diff(an) * n_names - np.diff(au) * n_num)[: allc.height]
        by_author = {}
        for a, s in zip(allc["author"].to_list(), st):
            if s > 0:
                by_author[a] = by_author.get(a, 0.0) + float(s)
        out[lin] = {"content_16_18": tot, "L": Lsh, "C": Csh, "days": days,
                    "content_by_author_35": dict(sorted(by_author.items(), key=lambda x: -x[1]))}
    return out


def git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout


def part_papers():
    base = ROOT / "data/raw/repos/github.com"
    vill = {"gpt-5-4": "best", "gemini-3-1-pro": "best", "deepseek-v32": "rest", "ai-village-agents": "org"}
    up = base / "terminator2-agent/agent-papers.git"
    cut = "2026-04-04T00:00:00+00:00"
    info, sets = {}, {}
    for o in vill:
        r = base / o / "agent-papers.git"
        lines = git(r, "log", "--first-parent", "--format=%H %cI %ae", "main").split("\n")
        fp = [ln.split() for ln in lines if ln]
        sets[o] = set(git(r, "rev-list", "main").split())
        info[o] = {"repo": r, "fp": fp}
    common = set.intersection(*sets.values())
    # newest common commit by committer date
    best_c, best_t = None, ""
    for o in vill:
        for sha, t, _ in info[o]["fp"]:
            if sha in common and t > best_t:
                best_c, best_t = sha, t
        break

    def tree(repo, sha):
        out = {}
        for ln in git(repo, "ls-tree", "-r", sha).split("\n"):
            if ln:
                meta, path = ln.split("\t", 1)
                out[path] = meta.split()[2]
        return out
    A = tree(info["gpt-5-4"]["repo"], best_c)
    ends, adopt, ncom = {}, {}, {}
    for o in vill:
        fp = [x for x in info[o]["fp"] if x[1] < cut]
        post = []
        for sha, t, ae in fp:
            if sha == best_c:
                break
            post.append((sha, t, ae))
        post = post[::-1]  # oldest first
        ncom[o] = {"post_A_first_parent": len(post),
                   "authors": sorted({ae.split("@")[0] for _, _, ae in post})[:8]}
        if not post:
            ends[o] = A
            continue
        ad = {}
        for sha, t, _ in post:
            T = tree(info[o]["repo"], sha)
            for p, b in T.items():
                if A.get(p) != b:
                    ad.setdefault((p, b), t)
        adopt[o] = ad
        ends[o] = tree(info[o]["repo"], post[-1][0])
    # upstream trees up to the cut (to source innovations)
    ul = [ln.split() for ln in git(up, "log", "--format=%H %cI", "main").split("\n") if ln]
    up_first = {}
    for sha, t in sorted(ul, key=lambda x: x[1]):
        if t >= cut:
            break
        for p, b in tree(up, sha).items():
            up_first.setdefault((p, b), t)
    keys = list(A)
    out = {"ancestor": best_c, "ancestor_t": best_t, "n_files_A": len(A), "commits": ncom, "vertical": {}, "pairs": {}}
    for o in vill:
        out["vertical"][o] = float(np.mean([ends[o].get(k) == A[k] for k in keys]))
    names = list(vill)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            xa = np.array([ends[a].get(k) == A[k] for k in keys])
            xb = np.array([ends[b].get(k) == A[k] for k in keys])
            same = np.array([ends[a].get(k) == ends[b].get(k) for k in keys])
            sh = {(p, bl) for p, bl in ends[a].items() if A.get(p) != bl and ends[b].get(p) == bl}
            src = 0
            for k in sh:
                ta, tb = adopt.get(a, {}).get(k), adopt.get(b, {}).get(k)
                tu = up_first.get(k)
                if tu is not None and ta is not None and tb is not None and tu <= min(ta, tb):
                    src += 1
            out["pairs"][f"{a}~{b}"] = {"rooms": f"{vill[a]}~{vill[b]}", "anc_same": float(same.mean()),
                                        "anc_both_unch": float((xa & xb).mean()),
                                        "excess": float(same.mean() - (xa & xb).mean()),
                                        "shared_innovations": len(sh), "upstream_first": src}
    return out


def part_estimates():
    import estimates as E
    r = json.loads(OUTF.read_text())
    src = "data/processed/H07-rpg-forks/r1b/results_r1b.json"
    rows = []
    g35 = next(x for x in r["ledger"]["by_goal"] if x["goal_no"] == 35)
    base = dict(goal_no=35, period_unit=E.map_unit(35), source=src, post_hoc=False, status="exploratory round 1b")
    rows.append(dict(base, statistic="cross_team_read_share", channel="chat (context ledger)", estimate=g35["share"],
                     n=g35["items"], n_kind="chat items read", ci_kind="none", role="native",
                     null="closed rooms: 0", method="share of agent chat items entering #best/#rest agents' calls sent by the other team (DQ6 teams)"))
    p6 = r["dq4"]["P6_35"]
    rows.append(dict(base, statistic="commits_per_capita_ratio_best_over_rest", channel="git (DQ4 agent work)",
                     estimate=p6["best"]["per_capita_work"] / p6["rest"]["per_capita_work"], n=p6["best"]["agent_work_35"] + p6["rest"]["agent_work_35"],
                     n_kind="commits", ci_kind="none", role="replication", null="P6: rest >= 1.5x best in total commits",
                     method="non-merge post-split commits in #35 that are DQ4 agent work, per DQ6 team member"))
    rows.append(dict(base, statistic="content_share_by_lead_designer", channel="git (keyed names + data numbers)",
                     estimate=r["lead"]["best"]["L"], n=r["lead"]["best"]["content_16_18"], n_kind="content keys changed",
                     ci_kind="none", role="native", null="lead designer's commit share C = %.2f" % r["lead"]["best"]["C"],
                     method="#best: share of inherited content keys changed 03-16..18 by the DQ6 lead designer of the room-day"))
    pr = r["papers"]["pairs"]["deepseek-v32~ai-village-agents"]
    rows.append(dict(goal_no=36, period_unit=E.map_unit(36), source=src, post_hoc=False, status="exploratory round 1b",
                     statistic="independent_lineage_excess", channel="git files (agent-papers fork family)", estimate=pr["excess"],
                     n=r["papers"]["n_files_A"], n_kind="ancestor files", ci_kind="none", role="native",
                     null="independent lineages: identity = P(both unchanged)",
                     method="identity of ancestor files between the #rest and org copies minus P(both unchanged), commits to 2026-04-03"))
    E.write_estimates(rows, hypothesis="H07", replace_keys=("statistic", "channel", "method", "role"))
    return {"rows": len(rows)}


def main():
    if os.environ.get("H07_DATA") != "r1b":
        raise SystemExit("round 1b: set H07_DATA=r1b")
    parts = sys.argv[1:] or ["copyinfo", "dq4", "p8", "ledger", "lead", "papers"]
    R1B.mkdir(parents=True, exist_ok=True)
    res = json.loads(OUTF.read_text()) if OUTF.exists() else {}
    for p in parts:
        res[p] = globals()[f"part_{p}"]()
        print(p, json.dumps(res[p], indent=1, default=str)[:2500], flush=True)
    OUTF.write_text(json.dumps(res, indent=1, default=str))
    prov = {"built_by": "hypotheses/H07-rpg-forks/analysis/round1b.py", "git_commit": None,
            "inputs": [{"source": "ai-village", "tables": ["ground_truth_labels", "work_commits", "call_windows",
                                                           "context_ledger_items", "chat_text (in memory only)",
                                                           "artifact_mentions", "artifacts", "calendar"]},
                       {"source": "data/raw/repos (on-disk clones, no fetch)", "repos": ["rpg-game*", "*/agent-papers"]}],
            "params": {"parts": sorted(res), "END37": END37.isoformat(), "papers_cut": "2026-04-04"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    from common import git_commit
    prov["git_commit"] = git_commit()
    (R1B / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
