"""Shared copying-channel test: does a project named in a message the agent has READ predict a switch to it, compared
with one posted but not yet read (in flight) or not mentioned? Mantel-Haenszel odds ratios over strata.

Moved from H06 (hypotheses/H06-neutral-cooperative-dynamics/analysis/round1b.py: _messages, _reads, mh_or,
copying_scope, copying; RE-D2 "Copying follows reading": OR 8.6 [4.5, 16.4] read vs posted-unread on attention labels).
The design is unchanged and works on any per-window project labels (attention, work, intention clusters):

  candidate   agent i labelled at windows t and t+1 of the same day; project q held at t by >= 1 other agent; q != i's
              label at t. Outcome Y = i holds q at t+1.
  class V     a chat message by another agent with a strict mention of q entered one of i's calls during window t
              (receiving call t_call in [ws_t, we_t); DQ1 ledger, `visibility.receipts`)
  class U     no V, and such a message was posted during t but had not entered i's context by the end of t (in flight;
              the H57 contemporaneous-convergence placebo, STANDARDS.md section 1)
  class N     neither
  strata      scope (period or unit) x abundance of q at t (1 / 2 / 3+ other holders); MH odds ratio with the
              Robins-Breslow-Greenland 95% CI for V vs N, V vs U and U vs N.

Table (data/processed/shared/project_mentions_chat.parquet, zstd, no text, ALL days, `holdout` flagged): one row per
(agent chat message, named project): msg (chat_core row), message_id, t, pt_date, goal_no, holdout, room, agent,
project (canonical repo name; files and sites map to their parent repo, as project_states). Strict mentions only
(artifact_mentions source == chat and how in url / output / bare).

Functions: project_messages, reads_for, copy_candidates, mh_or, copying_summary.

Usage: uv run python infra/shared/copying.py            (build project_mentions_chat.parquet)
       uv run python infra/shared/copying.py --verify   (rerun H06's copying test on its round-1b labels with the shared
                                                         code and compare with r1b/copying_r1b.json; read-only)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "RAYON_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import bisect  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, write_provenance  # noqa: E402
from visibility import holdout_flags, load_ro, receipts  # noqa: E402

SH = OUT
STRICT_HOW = ["url", "output", "bare"]
H06_R1B = ROOT / "data/processed/H06-neutral-cooperative-dynamics/r1b"


# ----------------------------------------------------------------------------------------------- inputs
def build_project_mentions() -> pl.DataFrame:
    import project_states as PS
    pm = PS.project_map()
    am = (pl.scan_parquet(SH / "artifact_mentions.parquet")
          .filter((pl.col("source").cast(pl.String) == "chat") & pl.col("how").cast(pl.String).is_in(STRICT_HOW)
                  & pl.col("message_id").is_not_null())
          .select("artifact", "message_id").collect())
    am = am.join(pm, on="artifact", how="inner").select("message_id", "project").unique()
    cc = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "room", "speaker_kind",
                                                             "agent"])
          .with_row_index("msg").filter(pl.col("speaker_kind").cast(pl.String) == "agent"))
    out = cc.join(am, on="message_id", how="inner")
    out = out.with_columns(holdout_flags(out).alias("holdout"))
    return out.select(pl.col("msg").cast(pl.UInt32), "message_id", "t", "pt_date", "goal_no", "holdout", "room",
                      pl.col("agent").cast(pl.Int8), "project").sort("msg", "project")


def project_messages(goals=None, exclude_holdout: bool = False) -> pl.DataFrame:
    """Agent chat messages with the projects they name (message_id, t, room, agent, goal_no, project, ...)."""
    df = pl.read_parquet(SH / "project_mentions_chat.parquet")
    if goals is not None:
        df = df.filter(pl.col("goal_no").is_in(list(goals)))
    if exclude_holdout:
        df = df.filter(~pl.col("holdout"))
    return df


def reads_for(goals, message_ids) -> pl.DataFrame:
    """(message_id, recipient, t_call): receiving calls of these messages among the calls of goal periods `goals`
    (H06's restriction: a message read in a later period is not a read here)."""
    r = receipts(message_ids, goal_nos=goals)
    return r.select("message_id", "recipient", "t_call")


# ----------------------------------------------------------------------------------------------- the test
def copy_candidates(lab: np.ndarray, agents: list, day: np.ndarray, win_start: list, win_end: list, label_name: dict,
                    msgs: pl.DataFrame, reads: pl.DataFrame):
    """Candidate rows for one scope.
    lab (T, N) int labels per window x agent (-1 = unlabelled), windows time-sorted; agents: agent codes of the columns;
    day (T,): day index of each window (transitions only within a day); win_start / win_end: window bounds (datetimes);
    label_name: label id -> project name (as in `project` of msgs); msgs: message_id, t, agent, project (agent chat
    messages of this scope); reads: message_id, recipient, t_call.
    Returns (rows, counts): rows = (abundance 1..3, class 'V'/'U'/'N', y 0/1); counts[class] = [switches, candidates]."""
    T, N = lab.shape
    ws, we = list(win_start), list(win_end)
    rd = reads.join(msgs.select("message_id").unique(), on="message_id", how="semi")
    rd_by = {}
    for mid, rc, tc in rd.select("message_id", "recipient", "t_call").iter_rows():
        d = rd_by.setdefault(mid, {})
        if rc not in d or tc < d[rc]:
            d[rc] = tc

    def widx(t_):
        i = bisect.bisect_right(ws, t_) - 1
        return i if 0 <= i < T and t_ < we[i] else None

    ai = {ag: i for i, ag in enumerate(agents)}
    V, posted = {}, {}
    for mid, tm_, snd, pr in msgs.select("message_id", "t", "agent", "project").iter_rows():
        tp = widx(tm_)
        if tp is not None:
            posted.setdefault(tp, []).append((mid, snd, pr))
        for rc, tr in rd_by.get(mid, {}).items():
            if rc == snd or rc not in ai:
                continue
            tw = widx(tr)
            if tw is not None:
                V.setdefault((tw, ai[rc]), set()).add(pr)
    rows = []
    counts = {"V": [0, 0], "U": [0, 0], "N": [0, 0]}
    for t in range(T - 1):
        if day[t] != day[t + 1]:
            continue
        held = {}
        for a in range(N):
            if lab[t, a] >= 0:
                held.setdefault(lab[t, a], set()).add(a)
        for a in range(N):
            if lab[t, a] < 0 or lab[t + 1, a] < 0:
                continue
            ag = agents[a]
            Va = V.get((t, a), set())
            Ua = set()
            for mid, snd, pr in posted.get(t, []):
                if snd == ag:
                    continue
                tr = rd_by.get(mid, {}).get(ag)
                if tr is None or tr >= we[t]:
                    Ua.add(pr)
            for q, hs in held.items():
                if q == lab[t, a]:
                    continue
                others = hs - {a}
                if not others:
                    continue
                name = label_name.get(int(q))
                cls = "V" if name in Va else ("U" if name in Ua else "N")
                y = int(lab[t + 1, a] == q)
                rows.append((min(len(others), 3), cls, y))
                counts[cls][0] += y
                counts[cls][1] += 1
    return rows, counts


def mh_or(tab):
    """Mantel-Haenszel odds ratio over strata; tab: list of (a, b, c, d) = (exp&Y, exp&~Y, ref&Y, ref&~Y).
    Robins-Breslow-Greenland 95% CI."""
    num = den = 0.0
    P = Q = R = 0.0
    for a, b, c, d in tab:
        n = a + b + c + d
        if n == 0:
            continue
        r_, s_ = a * d / n, b * c / n
        num += r_
        den += s_
        p_, q_ = (a + d) / n, (b + c) / n
        P += p_ * r_
        Q += p_ * s_ + q_ * r_
        R += q_ * s_
    if num == 0 or den == 0:
        return {"or": float("nan"), "lo": float("nan"), "hi": float("nan")}
    orr = num / den
    se = (P / (2 * num ** 2) + Q / (2 * num * den) + R / (2 * den ** 2)) ** 0.5
    return {"or": orr, "lo": float(np.exp(np.log(orr) - 1.96 * se)), "hi": float(np.exp(np.log(orr) + 1.96 * se)), "se_log": se}


def copying_summary(rows) -> dict:
    """rows: (scope, abundance, class, y). MH odds ratios over (scope, abundance) strata, plus counts."""
    summ = {}
    for e, ref in (("V", "N"), ("V", "U"), ("U", "N")):
        tab = []
        for s in sorted({r[0] for r in rows}):
            for k in (1, 2, 3):
                sub = [r for r in rows if r[0] == s and r[1] == k]
                tab.append((sum(1 for r in sub if r[2] == e and r[3] == 1), sum(1 for r in sub if r[2] == e and r[3] == 0),
                            sum(1 for r in sub if r[2] == ref and r[3] == 1), sum(1 for r in sub if r[2] == ref and r[3] == 0)))
        summ[f"OR_{e}_vs_{ref}"] = mh_or(tab)
    summ["n_candidates"] = {c: sum(1 for r in rows if r[2] == c) for c in "VUN"}
    summ["n_switches"] = {c: sum(1 for r in rows if r[2] == c and r[3] == 1) for c in "VUN"}
    summ["scopes"] = sorted({r[0] for r in rows})
    return summ


# ----------------------------------------------------------------------------------------------- build / verify
def main():
    t0 = time.time()
    df = build_project_mentions()
    p = SH / "project_mentions_chat.parquet"
    df.write_parquet(p, compression="zstd", compression_level=9)
    nh = df.filter(~pl.col("holdout"))
    summ = {"rows": df.height, "messages": int(df["message_id"].n_unique()), "rows_nonholdout": nh.height,
            "projects": int(df["project"].n_unique())}
    write_provenance("copying", ["artifact_mentions", "artifacts", "chat_core"],
                     {"mentions": "artifact_mentions source == chat, how in url/output/bare", "projects":
                      "project_states.project_map (files and sites -> parent repo)", "speakers": "agents only",
                      "holdout": "all days, flagged", "source": "hypotheses/H06-neutral-cooperative-dynamics/analysis/"
                      "round1b.py: _messages, copying (rule unchanged)", "summary": summ})
    print(f"project_mentions_chat.parquet: {df.height} rows, {p.stat().st_size / 1e6:.2f} MB, {time.time() - t0:.0f}s; "
          f"{json.dumps(summ)}", flush=True)


def _close(a, b, tol=1e-9):
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return abs(a - b) <= tol * max(1.0, abs(b))


def verify() -> dict:
    """H06's scopes and label sets (its round1b.load, imported read-only), shared copy_candidates, vs copying_r1b.json."""
    ref = json.loads((H06_R1B / "copying_r1b.json").read_text())
    scopes = sorted(ref["per_scope"], key=lambda s: ["G31", "G37", "G44", "G30", "G38", "G19", "G25"].index(s)
                    if s in ["G31", "G37", "G44", "G30", "G38", "G19", "G25"] else 99)
    sys.path.insert(0, str(ROOT))
    h06 = load_ro("h06_round1b_ro", ROOT / "hypotheses/H06-neutral-cooperative-dynamics/analysis/round1b.py")
    goals = sorted({int(h06.SCOPES[s][0][1:3]) for s in scopes})
    msgs = project_messages(goals)
    reads = reads_for(goals, msgs["message_id"].unique().to_list())
    half = dt.timedelta(minutes=15)
    res, pooled = {"per_scope": {}}, {"art": [], "work": []}
    n_bad = 0
    for s in scopes:
        wins, day, remap, labs, _ = h06.load(s)
        folder = h06.SCOPES[s][0]
        g = int(folder[1:3])
        for nm in ("art", "work"):
            df = labs[nm]
            if df.height == 0:
                continue
            proj = pl.read_parquet(H06_R1B / folder / f"projects_{nm}.parquet")
            names = dict(zip(proj["project_id"].to_list(), proj["project"].to_list()))
            lab, agents = h06.X.matrix(df, "project_id", remap, wins.height)
            tmid = wins["t_mid"].to_list()
            rows, counts = copy_candidates(lab, agents, day, [t - half for t in tmid], [t + half for t in tmid], names,
                                           msgs.filter(pl.col("goal_no") == g), reads)
            pooled[nm] += [(s, *x) for x in rows]
            mine = {k: {"switches": v[0], "candidates": v[1]} for k, v in counts.items()}
            theirs = {k: {"switches": v["switches"], "candidates": v["candidates"]}
                      for k, v in ref["per_scope"].get(s, {}).get(nm, {}).items()}
            ok = mine == theirs
            n_bad += not ok
            res["per_scope"][f"{s}/{nm}"] = "identical" if ok else {"shared": mine, "h06": theirs}
    for nm, rows in pooled.items():
        if not rows:
            continue
        mine = copying_summary(rows)
        theirs = ref["pooled"][nm]
        cmp = {k: all(_close(mine[k][x], theirs[k][x]) for x in theirs[k]) for k in ("OR_V_vs_N", "OR_V_vs_U", "OR_U_vs_N")}
        cmp["counts"] = mine["n_candidates"] == theirs["n_candidates"] and mine["n_switches"] == theirs["n_switches"]
        res[f"pooled_{nm}"] = cmp
        n_bad += not all(cmp.values())
        res[f"pooled_{nm}_OR_V_vs_U"] = mine["OR_V_vs_U"]["or"]
    res["identical"] = n_bad == 0
    print(json.dumps(res, indent=1, default=float), flush=True)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
