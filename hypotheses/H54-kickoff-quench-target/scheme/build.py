"""H54 scheme: build data/processed/H54-kickoff-quench-target/ from shared tables (no text stored).

Outputs
  kick_msgs.parquet     message_id, goal_no, room, t, length (kickoff messages, goal_fields' rule re-derived)
  kickoffs.parquet      per (goal_no, room | null = all rooms): t0, n_msgs, words and specificity counts, S_text,
                        S_count (z-scored over eligible kickoffs), fallback
  stmt.parquet          statements used by H54: goal_no (target period p), day (1 = kickoff day, 0 = previous period's
                        last non-holdout day), pt_date, agent, kind, t, room, srow, pre_kick, regime_src
  stmt_z.npy            (n, 32) fp16: unit(W_{r_p}(raw)) in the TARGET period's regime basis
  stmt_zs.npy           (n, 32) fp16: DQ5 style-residualized (per period) copy; NaN where the statement's regime != r_p
  projects.parquet      H31 (block, project) rows + own-rule day-1 candidate projects with artifact-id flags
  human_msgs.parquet    mid-period human messages >= 250 chars (HH180): ids, times, specificity, ledger receptivity
  first_plans.parquet   first concrete agent plan per (period, room | all) on day 1 (HH181)
  g26_leader.json       the #26 leader's goal announcement (message id, time)
Text (kickoffs, goal texts, human messages, plan detection, the #26 announcement) is held in memory only.

Usage: uv run python hypotheses/H54-kickoff-quench-target/scheme/build.py [--allow-holdout]   (confirm.py only)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import math  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import h54lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import URL_RE, load_goals, mention_regexes, holdout_mask  # noqa: E402
from goal_fields import kickoff_messages, strip_boilerplate  # noqa: E402
from project_states import project_map  # noqa: E402

STRICT = ["url", "output", "bare"]
GENERIC = {"village", "agent", "agents", "github", "gitlab", "www", "main", "master", "repo", "project", "projects",
           "test", "tests", "site", "page", "pages", "docs", "the", "and", "for", "with", "from", "your", "html", "index",
           "http", "https", "netlify", "vercel", "app", "apps", "com", "org", "io", "net", "dev", "blob", "tree", "src",
           "readme", "public", "data", "file", "files", "edit", "view", "google", "document", "drive", "folder",
           "spreadsheets", "presentation", "forms", "sheet", "sheets", "new", "final", "draft", "home", "aivillage",
           "aidigest", "digest", "agentvillage", "ai-village-agents"}
WEEKDAYS = r"monday|tuesday|wednesday|thursday|friday|saturday|sunday"
MONTHS = r"january|february|march|april|may|june|july|august|september|october|november|december"
RX = {
    "numbers": re.compile(r"(?<![\w])[$€£]?\d[\d,.:/]*%?"),
    "deadlines": re.compile(rf"\b(?:{WEEKDAYS}|{MONTHS}|today|tomorrow|tonight|deadline|deadlines|hours?|minutes?|weeks?|"
                            r"days?|end of|by eod|eod)\b|\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b|\b(?:pt|pst|pdt|utc|et)\b", re.I),
    "roles": re.compile(r"\b(?:teams?|teammates?|judges?|leaders?|captains?|roles?|moderators?|hosts?|partners?|saboteurs?|"
                        r"villagers?|voters?|candidates?|referees?|organi[sz]ers?|coordinators?|lead)\b|#\w+", re.I),
}
WORD = re.compile(r"[A-Za-z0-9][\w'’-]*")
CAP = re.compile(r"(?<![.!?\n:]\s)(?<!^)\b[A-Z][\w'’-]+")


def spec_counts(text: str, agent_rx: list[re.Pattern], strict_artifacts: int = 0) -> dict:
    """Specificity counts. Agent names are counted as roles and masked first, so their version numbers
    (e.g. '4.7') and capitals do not also count as numbers or named entities (fix made before any outcome run)."""
    words = len(WORD.findall(text))
    agents = 0
    masked = text
    for rx in agent_rx:
        agents += len(rx.findall(masked))
        masked = rx.sub(" agentname ", masked)
    ents = 0
    for sent in re.split(r"(?<=[.!?])\s+|\n+", masked):
        toks = WORD.findall(sent)
        ents += sum(1 for t in toks[1:] if t[:1].isupper() and t not in {"I", "I'm", "I'll", "AI", "OK"})
    return {"words": words, "numbers": len(RX["numbers"].findall(masked)), "entities": ents,
            "artifacts": len(URL_RE.findall(text)) + strict_artifacts,
            "roles": len(RX["roles"].findall(masked)) + agents, "deadlines": len(RX["deadlines"].findall(masked))}


CLASSES = ["numbers", "entities", "artifacts", "roles", "deadlines"]


def add_scores(df: pl.DataFrame, ref: pl.DataFrame | None = None) -> pl.DataFrame:
    """S_text = mean z of log1p(count per 100 words); S_count = mean z of log1p(count). z over `ref` rows (default df)."""
    ref = df if ref is None else ref
    out = df
    zt, zc = [], []
    for c in CLASSES:
        dens = lambda f: (f[c] / f["words"].clip(1) * 100).log1p()  # noqa: E731
        cnt = lambda f: f[c].log1p()  # noqa: E731
        for fn, acc, nm in ((dens, zt, "d"), (cnt, zc, "c")):
            r = fn(ref)
            mu, sd = float(r.mean()), float(r.std() or 1.0)
            out = out.with_columns(((fn(out) - mu) / (sd if sd > 0 else 1.0)).alias(f"z{nm}_{c}"))
            acc.append(f"z{nm}_{c}")
    return out.with_columns(pl.mean_horizontal(zt).alias("S_text"), pl.mean_horizontal(zc).alias("S_count"))


def name_tokens(project: str) -> set[str]:
    s = project.lower()
    s = re.sub(r"^(https?://)?", "", s)
    parts = s.split("/")
    host = parts[0]
    path = parts[1:]
    if host in ("github.com", "gitlab.com") and path:
        path = path[1:]  # drop owner
        if path[:1] == ["village"]:
            path = path[1:]
    toks = []
    if host.endswith("github.io") or host.endswith("netlify.app") or host.endswith("vercel.app") or host.endswith("pages.dev"):
        toks += re.split(r"[-_.]", host.split(".")[0]) if not host.endswith("github.io") else []
    elif host not in ("github.com", "gitlab.com", "docs.google.com", "drive.google.com"):
        toks += re.split(r"[-_.]", host.rsplit(".", 1)[0])
    for p in path:
        toks += re.split(r"[-_.:]", p)
    out = set()
    for t in toks:
        t = t.strip()
        if len(t) < 4 or t.isdigit() or t in GENERIC or re.fullmatch(r"[0-9a-f]{8,}", t) or re.search(r"\d{3,}", t):
            continue
        if len(t) > 20 and not re.search(r"[aeiou]{1}", t):
            continue
        out.add(t)
    return out


def text_tokens(text: str) -> set[str]:
    toks = {t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9]+", text)}
    toks |= {t[:-1] for t in toks if t.endswith("s") and len(t) > 4}
    return toks


def tok_match(ptoks: set[str], ttoks: set[str]) -> int:
    n = 0
    for t in ptoks:
        if t in ttoks or (t.endswith("s") and t[:-1] in ttoks):
            n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-holdout", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    t0 = time.time()
    out = Path(a.out) if a.out else L.OUT
    out.mkdir(parents=True, exist_ok=True)
    ah = a.allow_holdout

    cal_all = L.calendar(allow_holdout=True)
    cal = cal_all if ah else cal_all.filter(~pl.col("ho"))
    G = L.goals()
    elig = L.eligible(allow_holdout=ah)
    goal_text = {g["goal_no"]: g["goal"] for g in load_goals()}
    roster = pl.read_parquet(L.SHARED / "roster.parquet")
    agent_rx = list(mention_regexes([{"id": r["agent_id"], "name": r["name"]} for r in roster.iter_rows(named=True)]).values())
    chat_h = (pl.read_parquet(L.SHARED / "chat_core.parquet", columns=["message_id", "t", "pt_date", "room", "speaker_kind", "length"])
              .filter(pl.col("speaker_kind").cast(pl.String) == "human"))
    text = pl.read_parquet(L.SHARED / "chat_text.parquet", columns=["message_id", "text"])
    am = pl.read_parquet(L.SHARED / "artifact_mentions.parquet")
    pmap = project_map()
    am_s = am.filter(pl.col("how").cast(pl.String).is_in(STRICT)).join(pmap, on="artifact", how="inner")

    # ------------------------------------------------------------------ kickoff messages and specificity
    first = cal_all.group_by("goal_no").agg(pl.col("pt_date").min().alias("d0")).sort("goal_no")
    d0 = dict(first.iter_rows())
    km_rows, ko_rows = [], []
    kick_tokens, kick_t0, kick_ids = {}, {}, {}
    for p in elig:
        k, fb, ws = kickoff_messages(cal_all.select("pt_date", "win_start"), chat_h, d0[p])
        k = k.sort("t")
        kick_t0[p] = k["t"][0]
        kick_ids[p] = k["message_id"].to_list()
        for r in k.iter_rows(named=True):
            km_rows.append({"message_id": r["message_id"], "goal_no": p, "room": r["room"], "t": r["t"], "length": r["length"]})
        kt = k.join(text, on="message_id", how="left")
        sa_all = am_s.filter(pl.col("message_id").is_in(kick_ids[p]) & (pl.col("speaker_kind").cast(pl.String) == "human"))
        bodies = {}
        for room, grp in kt.group_by("room", maintain_order=True):
            bodies[int(room[0])] = " ".join(strip_boilerplate(x or "") for x in grp.sort("t")["text"].to_list())
        whole = " ".join(bodies[r] for r in bodies)
        kick_tokens[p] = text_tokens(whole) | text_tokens(goal_text[p])
        for room, body in [(None, whole)] + ([(r, b) for r, b in bodies.items()] if len(bodies) > 1 else []):
            ids = kick_ids[p] if room is None else kt.filter(pl.col("room") == room)["message_id"].to_list()
            nart = sa_all.filter(pl.col("message_id").is_in(ids))["artifact"].n_unique()
            c = spec_counts(body, agent_rx, nart)
            ko_rows.append({"goal_no": p, "room": room, "t0": k["t"][0], "n_msgs": len(ids), "fallback": fb,
                            "strict_artifacts": nart, "goal_words": len(WORD.findall(goal_text[p])), **c})
        del kt, bodies, whole
    km = pl.DataFrame(km_rows)
    km.write_parquet(out / "kick_msgs.parquet")
    ko = pl.DataFrame(ko_rows, schema_overrides={"room": pl.Int8})
    allrows = ko.filter(pl.col("room").is_null())
    ko = add_scores(ko, ref=allrows)
    ko.write_parquet(out / "kickoffs.parquet")
    print(f"kickoffs: {allrows.height} periods ({time.time() - t0:.0f}s)")

    # ------------------------------------------------------------------ statements
    st = L.statements().filter(pl.col("agent") != L.CLAUDE_CODE)
    cal_idx = cal_all.with_columns(pl.int_range(1, pl.len() + 1).over("goal_no").alias("day")).select("pt_date", "goal_no", "day", "ho")
    goal_regime = {p: L.period_regime(p) for p in range(1, 52)}
    ZS_all = np.load(L.ED / "statements_style_resid_period32_bge_small.npy", mmap_mode="r")
    parts, Zs, ZSs = [], [], []
    for p in elig:
        r = goal_regime[p]
        cur = st.filter(pl.col("goal_no") == p).join(cal_idx.filter(pl.col("goal_no") == p).drop("goal_no"), on="pt_date", how="inner")
        if not ah:
            cur = cur.filter(~pl.col("ho"))
        cur = cur.with_columns(pl.lit(p).cast(pl.Int8).alias("tgt"))
        prev = None
        q = p - 1
        if q >= 1 and q not in L.EXCLUDE:
            qd = cal_all.filter(pl.col("goal_no") == q)
            if not ah:
                qd = qd.filter(~pl.col("ho"))
            if qd.height and (ah or not holdout_mask([qd["pt_date"][-1]], [q])[0]):
                last = qd["pt_date"][-1]
                prev = (st.filter((pl.col("goal_no") == q) & (pl.col("pt_date") == last))
                        .with_columns(pl.lit(0).cast(pl.Int64).alias("day"), pl.lit(False).alias("ho"), pl.lit(p).cast(pl.Int8).alias("tgt")))
        cols = ["srow", "kind", "src_row", "agent", "t", "pt_date", "room", "goal_no", "regime", "day", "tgt"]
        seg = cur.select(cols) if prev is None else pl.concat([cur.select(cols), prev.select(cols)], how="vertical_relaxed")
        seg = seg.with_columns(((pl.col("day") == 1) & (pl.col("t") < kick_t0[p])).alias("pre_kick"),
                               pl.col("regime").alias("regime_src"))
        raw = L.raw_for(seg)
        Zs.append(L.whiten_unit(raw, r).astype(np.float16))
        zs = np.full((seg.height, L.D), np.nan, dtype=np.float32)
        same = (seg["regime_src"] == r).to_numpy()
        srows = seg["srow"].to_numpy()
        if same.any():
            o = np.argsort(srows[same])
            zs[np.flatnonzero(same)[o]] = np.asarray(ZS_all[srows[same][o]], dtype=np.float32)
        ZSs.append(zs.astype(np.float16))
        parts.append(seg.select(pl.col("tgt").alias("goal_no"), "day", "pt_date", "agent", "kind", "t", "room", "srow",
                                "pre_kick", "regime_src", pl.col("goal_no").alias("src_goal")))
    stmt = pl.concat(parts, how="vertical_relaxed")
    stmt.write_parquet(out / "stmt.parquet")
    np.save(out / "stmt_z.npy", np.vstack(Zs))
    np.save(out / "stmt_zs.npy", np.vstack(ZSs))
    print(f"statements: {stmt.height} rows ({time.time() - t0:.0f}s)")

    # ------------------------------------------------------------------ projects
    am_agent = am_s.filter(pl.col("speaker_kind").cast(pl.String) == "agent")
    am_agent = am_agent.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    am_agent = am_agent.join(cal_all.select("pt_date", "goal_no", "ho"), on="pt_date", how="inner")
    if not ah:
        am_agent = am_agent.filter(~pl.col("ho"))
    am_hum = am_s.filter(pl.col("speaker_kind").cast(pl.String) == "human")
    plans = first_plans(elig, kick_t0, cal_all, am_s, ah)
    plans.write_parquet(out / "first_plans.parquet")
    plan_ids = {(r["goal_no"], r["scope"]): r["message_id"] for r in plans.iter_rows(named=True)}

    def flags(p: int, project: str) -> dict:
        tk0 = kick_t0[p]
        ptoks = name_tokens(project)
        strict_k = am_hum.filter(pl.col("message_id").is_in(kick_ids[p]) & (pl.col("project") == project)).height > 0
        loose_k = tok_match(ptoks, kick_tokens[p] - text_tokens(goal_text[p])) if ptoks else 0
        loose_g = tok_match(ptoks, text_tokens(goal_text[p])) if ptoks else 0
        mp = am_agent.filter(pl.col("project") == project)
        pre = mp.filter(pl.col("t") < tk0).height > 0
        prevdays = cal_all.filter((pl.col("goal_no") == p - 1))
        if not ah:
            prevdays = prevdays.filter(~pl.col("ho"))
        last2 = prevdays["pt_date"].to_list()[-2:] if (p - 1) not in L.EXCLUDE else []
        carry = mp.filter(pl.col("pt_date").is_in(last2)).height > 0 if last2 else None
        day1 = d0[p]
        hum1 = am_hum.filter((pl.col("project") == project)
                             & (pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String) == day1)).height > 0
        pid = plan_ids.get((p, "all"))
        plan_named = am_s.filter((pl.col("message_id") == pid) & (pl.col("project") == project)).height > 0 if pid else False
        art = pmap.filter(pl.col("project") == project)["artifact"].to_list()
        return {"artifact": int(min(art)) if art else None, "n_tokens": len(ptoks), "named_strict": strict_k,
                "named_loose_kick": loose_k > 0, "named_goal": loose_g > 0,
                "named": bool(strict_k or loose_k > 0 or loose_g > 0), "pre_existing": pre, "carry_over": carry,
                "human_day1": hum1, "plan_named": plan_named}

    prow = []
    ev = pl.read_parquet(L.H31 / "events_ep_w30.parquet")
    for p in sorted(set(ev["goal_no"].to_list())):
        if p not in elig:
            continue
        sp = pl.read_parquet(L.H31 / f"G{p:02d}" / "states_project_w30.parquet").filter(pl.col("label") > 0)
        lab = sp.group_by("label").agg(pl.col("project").mode().first(), pl.col("project").n_unique().alias("nu"))
        assert lab["nu"].max() == 1, (p, "label->project not 1:1")
        lmap = dict(zip(lab["label"].to_list(), lab["project"].to_list()))
        for e in ev.filter(pl.col("goal_no") == p).iter_rows(named=True):
            cls = ("none" if not e["consensus"] else "gradual" if not e["frozen"]
                   else "kickoff_frozen" if (e["t0_h"] or 0) <= 0.75 + 1e-6 else "instant")
            prow.append({"src": "H31", "goal_no": p, "room": e["room"], "label": e["label"], "cls": cls,
                         "t0_h": e["t0_h"], **flags(p, lmap[e["label"]])})
    # own rule: day-1 dominant projects on shared deterministic labels (all eligible periods with labels)
    ps = pl.read_parquet(L.SHARED / "project_states.parquet").filter((pl.col("w_min") == 30) & (pl.col("sources").cast(pl.String) == "all"))
    if not ah:
        ps = ps.filter(~pl.col("holdout"))
    for p in elig:
        q = ps.filter(pl.col("goal_no") == p).with_columns(pl.col("project").cast(pl.String))
        if q.height == 0:
            continue
        if goal_regime[p] == "I":
            q = q.with_columns(pl.lit(0).cast(pl.Int8).alias("room"))
        q = q.filter(pl.col("agent") != L.CLAUDE_CODE)
        for room, qr in q.group_by("room", maintain_order=True):
            cand = qr.group_by("project").agg(pl.col("agent").n_unique().alias("na"), pl.len().alias("nw")).filter((pl.col("na") >= 2) & (pl.col("nw") >= 2))
            if cand.height == 0:
                continue
            d1 = qr.filter(pl.col("pt_date") == d0[p])
            wins = d1.group_by("win").agg(pl.col("agent").n_unique().alias("nl")).filter(pl.col("nl") >= 3).sort("win").head(2)["win"].to_list()
            dom = set()
            for w in wins:
                ww = d1.filter(pl.col("win") == w)
                nl = ww["agent"].n_unique()
                cnt = ww.group_by("project").agg(pl.col("agent").n_unique().alias("k"))
                dom |= set(cnt.filter((pl.col("k") >= 3) & (pl.col("k") >= 0.5 * nl))["project"].to_list())
            for pr in cand["project"].to_list():
                prow.append({"src": "own", "goal_no": p, "room": int(room[0]), "label": None,
                             "cls": "day1_dominant" if pr in dom else ("day1_scored" if wins else "no_day1_window"),
                             "t0_h": None, **flags(p, pr)})
    projects = pl.DataFrame(prow, infer_schema_length=None)
    projects.write_parquet(out / "projects.parquet")
    print(f"projects: {projects.height} rows ({time.time() - t0:.0f}s)")

    # ------------------------------------------------------------------ human messages (HH180)
    kc = pl.read_parquet(L.SHARED / "kicks_classified.parquet").filter(
        (pl.col("kind").cast(pl.String) == "human_message") & (pl.col("subkind").cast(pl.String) != "kickoff"))
    hm = kc.join(chat_h.select("message_id", "length"), on="message_id", how="inner").filter(pl.col("length") >= 250)
    hm = hm.filter(pl.col("goal_no").is_in(elig) & ~pl.col("message_id").is_in(km["message_id"].to_list()))
    hm = hm.with_columns(pl.Series("ho", holdout_mask(hm["pt_date"].to_list(), hm["goal_no"].to_list())))
    if not ah:
        hm = hm.filter(~pl.col("ho"))
    ws = cal_all.select("pt_date", "win_start", "goal_no")
    hm = hm.join(ws.select("pt_date", "win_start"), on="pt_date", how="left")
    day1_start = {p: cal_all.filter(pl.col("pt_date") == d0[p])["win_start"][0] for p in elig}
    hm = hm.filter(~((pl.col("pt_date") == pl.col("goal_no").replace_strict(d0, default=None))
                     & (pl.col("t") < pl.col("goal_no").replace_strict(day1_start, default=None) + dt.timedelta(hours=2))))
    ht = hm.select("message_id").join(text, on="message_id", how="left")
    hrows = []
    sa_h = am_hum.group_by("message_id").agg(pl.col("artifact").n_unique().alias("na"))
    nart = dict(zip(sa_h["message_id"].to_list(), sa_h["na"].to_list()))
    for mid, tx in ht.iter_rows():
        hrows.append({"message_id": mid, **spec_counts(tx or "", agent_rx, nart.get(mid, 0))})
    del ht
    hspec = pl.DataFrame(hrows)
    hm = hm.join(hspec, on="message_id", how="left")
    hm = add_scores(hm)
    # ledger receptivity
    items = pl.read_parquet(L.SHARED / "context_ledger_items.parquet", columns=["turn_id", "message_id", "age_s"]).filter(
        pl.col("message_id").is_in(hm["message_id"].to_list()))
    turns = pl.read_parquet(L.SHARED / "context_ledger_turns.parquet", columns=["turn_id", "agent"])
    items = items.join(turns, on="turn_id", how="left").filter(pl.col("agent") != L.CLAUDE_CODE)
    rec = items.group_by("message_id").agg(pl.col("agent").n_unique().alias("n_read"),
                                           pl.col("agent").filter(pl.col("age_s") <= 1800).n_unique().alias("n_read30"),
                                           pl.col("age_s").min().alias("first_read_s"))
    hm = hm.join(rec, on="message_id", how="left").with_columns(
        (pl.col("n_read30") / pl.col("n_read").clip(1)).alias("receptive"))
    hm.select("message_id", "t", "pt_date", "goal_no", "room", "subkind", "targeted", "length", "words", *CLASSES,
              "S_text", "S_count", "n_read", "n_read30", "first_read_s", "receptive").write_parquet(out / "human_msgs.parquet")
    print(f"human messages: {hm.height} ({time.time() - t0:.0f}s)")

    # ------------------------------------------------------------------ #26 leader announcement
    if 26 in elig:
        chat_a = pl.read_parquet(L.SHARED / "chat_core.parquet", columns=["message_id", "t", "speaker_kind", "agent", "length"]).filter(
            (pl.col("agent") == 17) & (pl.col("t") > dt.datetime(2026, 1, 5, 19, 35, 22, tzinfo=dt.timezone.utc))
            & (pl.col("t") < dt.datetime(2026, 1, 6, 6, 0, tzinfo=dt.timezone.utc)))
        ct = chat_a.join(text, on="message_id").sort("t")
        pick = None
        for r in ct.iter_rows(named=True):
            tx = r["text"] or ""
            if len(WORD.findall(tx)) >= 60 and re.search(r"\bgoal\b", tx, re.I) and re.search(r"\b(game|fiction|story|interactive|adventure)\b", tx, re.I):
                pick = r
                break
        L.write_json(out / "g26_leader.json", {"message_id": pick["message_id"] if pick else None,
                                               "t": str(pick["t"]) if pick else None, "agent": 17,
                                               "rule": "first agent-17 message after the 19:35:22 result with >= 60 words, 'goal' and a game/fiction word"})
        del ct
    L.provenance("scheme/build.py", ["goal_fields (goals.parquet, goal_vectors.npy)", "statements + chat/intentions bge-small",
                                     "statements_style_resid_period32_bge_small (DQ5)", "chat_core", "chat_text (in memory)",
                                     "village_goals (in memory)", "artifact_mentions", "artifacts", "project_states",
                                     "H31 events_ep_w30 + G*/states_project_w30 (read-only)", "kicks_classified",
                                     "context_ledger_items", "context_ledger_turns", "text_features", "calendar", "roster"],
                 {"allow_holdout": ah, "eligible": elig, "excluded": sorted(L.EXCLUDE), "whitening": "target period regime, d=32",
                  "strict_how": STRICT})
    print(f"done in {time.time() - t0:.0f}s")


def first_plans(elig, kick_t0, cal_all, am_s, ah) -> pl.DataFrame:
    tf = pl.read_parquet(L.SHARED / "text_features.parquet", columns=["message_id", "agent", "t", "pt_date", "goal_no", "room",
                                                                       "words", "f_lines", "f_bullet_share"])
    strict_msgs = set(am_s.filter((pl.col("speaker_kind").cast(pl.String) == "agent") & (pl.col("source").cast(pl.String) == "chat"))["message_id"].to_list())
    d0 = dict(cal_all.group_by("goal_no").agg(pl.col("pt_date").min()).iter_rows())
    rows = []
    for p in elig:
        x = tf.filter((pl.col("goal_no") == p) & (pl.col("pt_date") == d0[p]) & (pl.col("t") > kick_t0[p]) & (pl.col("agent") != L.CLAUDE_CODE)).sort("t")
        x = x.with_columns((pl.col("f_bullet_share") * pl.col("f_lines").exp()).round().alias("bullets"),
                           pl.col("message_id").is_in(list(strict_msgs)).alias("has_art"))
        x = x.with_columns((pl.col("has_art") | ((pl.col("words") >= 60) & (pl.col("bullets") >= 3))).alias("concrete"))
        scopes = [("all", x)] + [(f"room{int(r[0])}", g) for r, g in x.group_by("room", maintain_order=True)] if x["room"].n_unique() > 1 else [("all", x)]
        for scope, g in scopes:
            c = g.filter(pl.col("concrete"))
            if c.height == 0:
                continue
            r = c.row(0, named=True)
            rows.append({"goal_no": p, "scope": scope, "message_id": r["message_id"], "agent": r["agent"], "t": r["t"],
                         "room": r["room"], "words": r["words"], "has_art": r["has_art"], "bullets": r["bullets"],
                         "rank_in_day": int(g["message_id"].to_list().index(r["message_id"])) + 1,
                         "min_after_kick": (r["t"] - kick_t0[p]).total_seconds() / 60})
    return pl.DataFrame(rows)


if __name__ == "__main__":
    main()
