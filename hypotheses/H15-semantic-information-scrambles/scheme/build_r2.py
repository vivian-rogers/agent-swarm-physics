"""H15 round 2 (2026-10-05): per-call features, erasure events and memory-note windows for R1-R3.

    uv run python hypotheses/H15-semantic-information-scrambles/scheme/build_r2.py

Writes data/processed/H15-semantic-information-scrambles/r2/:
  events.parquet   forced erasures F and pseudo-erasures P (regime III; channel_pointers' rules) with outcomes
                   (V20, V3, V6, W10, first write), V_pre, own artifact A_prev, trail classes (R1b), first-read classes
                   L / M / Gp / Gn and U35 (R2), and the re-acquisition statistics of calls 1-5 (R1a)
  segs.parquet     consolidation-opened segments of regime III with the read-or-search share of calls 1-5 (R1c)
  newcomer_days.parquet  per agent-day read-or-search share per call (R1c newcomers)
  notes.parquet    regime-III consolidation notes with hashed terms and the hashed term sets of the segment the note
                   closes (pre) and opens (post), restricted to the period's note vocabulary (R3)
  classifier_check.json  agreement of this round's read flag with H44's call categories (read-only data check)
  _provenance.json (key build_r2)
No text is stored: file objects and terms are 64-bit blake2b hashes. Non-reserved days only (load_calls drops reserved
calls; auxiliary rows are admitted with channel_pointers.admit_aux; refuse_holdout on every output).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS", "POLARS_MAX_THREADS", "RAYON_NUM_THREADS"):
    os.environ[_v] = "2"

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from h15common import OUT_R1, ROOT, SH, git_commit, refuse_holdout, REVISION  # noqa: E402

sys.path.insert(0, str(ROOT / "infra/shared"))
import channel_pointers as CP  # noqa: E402

import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import time  # noqa: E402
from collections import Counter  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

OUT = OUT_R1 / "r2"
OUT.mkdir(parents=True, exist_ok=True)
T0 = time.time()
R3_START = dt.datetime(2026, 3, 24, 7, tzinfo=dt.timezone.utc)
WIN, MIN_WIN, PRE_V, PRE_OBJ, PRE_L = 20, 10, 20, 20, 10


def log(*a):
    print(f"[{time.time() - T0:7.1f}s]", *a, flush=True)


def h64(s: str) -> int:
    return int.from_bytes(hashlib.blake2b(s.encode(), digest_size=8).digest(), "little", signed=True)


# ------------------------------------------------------------------------------------------- command classifier
LOCAL_READ = {"cat", "head", "tail", "less", "more", "grep", "egrep", "fgrep", "rg", "find", "ls", "tree", "wc", "stat",
              "diff", "jq", "awk", "pwd", "which", "file", "du", "realpath", "readlink", "sort", "uniq", "cut", "nl",
              "xxd", "md5sum", "sha256sum", "column", "basename", "dirname", "sed"}
GIT_READ = {"status", "log", "show", "diff", "branch", "remote", "rev-parse", "ls-files", "blame", "reflog", "describe",
            "shortlog"}
GIT_REMOTE = {"fetch", "pull", "clone", "ls-remote"}
GH_READ = {"view", "list", "status", "api", "search", "diff", "checks"}
NEUTRAL = {"cd", "export", "set", "source", "echo", "printf", "true", "clear", "date", "sleep", "unset", "alias", "."}
NOTES_RX = re.compile(r"(note|memory|memo|todo|handoff|journal|diary|scratch|progress|checklist|context|plan|session)",
                      re.I)
URL_RX = re.compile(r"https?://\S+")
SPLIT_RX = re.compile(r"&&|\|\||;|\n|\|")
EXT = ("py|md|json|html|htm|js|mjs|ts|tsx|jsx|css|txt|csv|tsv|yml|yaml|toml|sh|sql|ipynb|xml|svg|png|jpg|jpeg|gif|pdf|"
       "tex|rs|go|java|c|h|cpp|rb|php|log|cfg|ini|lock|jsonl|parquet|db|sqlite|mdx|vue|svelte|scss")
PATH_RX = re.compile(r"(?:[\w.~@+-]*/)+[\w.@+-]+|[\w@+-]+\.(?:" + EXT + r")\b", re.I)
ASSIGN_RX = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def classify(cmd: str) -> tuple[bool, bool, list[int]]:
    """(read, notes_read, file-object hashes) for one bash command text. read = every non-neutral simple command is a
    local or remote read (write flags are applied by the caller). Objects = last two components of path-like tokens."""
    if not cmd:
        return False, False, []
    c = URL_RX.sub(" ", cmd)
    objs = []
    for m in PATH_RX.findall(c):
        p = m.strip("'\"`,:()[]{}<>").lstrip("./~")
        if not p or p.startswith("dev/null") or p in ("dev", "tmp", "usr", "bin"):
            continue
        parts = [x for x in p.lower().split("/") if x and x not in (".", "..")]
        if not parts or len(parts[-1]) < 3:
            continue
        objs.append("/".join(parts[-2:]))
    n_read, n_other, notes = 0, 0, False
    for piece in SPLIT_RX.split(cmd):
        toks = piece.strip().split()
        while toks and (ASSIGN_RX.match(toks[0]) or toks[0] in ("sudo", "env", "time", "nohup")):
            toks = toks[1:]
        if toks and toks[0] == "timeout" and len(toks) > 2:
            toks = toks[2:]
        if not toks or toks[0].startswith("#"):
            continue
        h = toks[0].rsplit("/", 1)[-1]
        if h in NEUTRAL:
            continue
        rd = False
        if h in LOCAL_READ:
            rd = not (h == "sed" and any(t.startswith("-i") for t in toks[1:])) and ">" not in piece
        elif h == "git" and len(toks) > 1:
            sub = next((t for t in toks[1:] if not t.startswith("-") and "=" not in t), "")
            rd = sub in GIT_READ or sub in GIT_REMOTE
        elif h in ("curl", "wget", "http"):
            rd = not re.search(r"(-X\s*(POST|PUT|PATCH|DELETE)|\s-d\s|--data|\s-F\s|--form|--upload|\s-T\s|-o\s|-O\b)",
                               piece)
        elif h in ("gh", "glab") and len(toks) > 2:
            rd = toks[2] in GH_READ and not re.search(r"(-X\s*(POST|PUT|PATCH|DELETE)|\s-f\s|\s-F\s|--method)", piece)
        if rd:
            n_read += 1
            if any(NOTES_RX.search(t.rsplit("/", 1)[-1]) for t in toks[1:] if not t.startswith("-")):
                notes = True
        else:
            n_other += 1
    read = n_read > 0 and n_other == 0
    return read, read and notes, [h64(o) for o in set(objs)]


# ------------------------------------------------------------------------------------------- term tokenizer (R3)
STOP = set("""
this that with from then next session continue check verify work after before into have will should also more each only
when them they their there here what which while about above below again until make sure done still need needs using used
first last today tomorrow time current currently resume start finish complete completed keep plus were been being does
doing over under same such than very just most other some your yours ours mine like want well back down even ever every
much many must shall would could might upon onto within without across along around among between because since though
although whether either neither both once ready step steps item items thing things note notes plan plans goal goals task
tasks day days hour hours minute minutes morning afternoon evening tonight week weeks progress update updates updated
status remaining remain pending todo follow following followup ensure confirm confirmed confirming verified verifying
checked checking working continue continuing continued resume resuming
""".split())
TOK_RX = re.compile(r"[a-z0-9]+")


def terms_of(text: str) -> set[str]:
    if not text:
        return set()
    out = set()
    for t in TOK_RX.findall(text.lower()):
        has_a = any(ch.isalpha() for ch in t)
        has_d = any(ch.isdigit() for ch in t)
        if not has_a or t in STOP:
            continue
        if len(t) >= 4 or (len(t) >= 2 and has_d):
            out.add(t)
    return out


def hset(text: str) -> np.ndarray:
    return np.array(sorted(h64(t) for t in terms_of(text)), dtype=np.int64)


# ------------------------------------------------------------------------------------------- build
def main():
    calls = CP.load_calls()
    # deterministic order (load_calls sorts by agent, t_first; ties broken here by turn_id)
    calls = (calls.drop("g", "seq", "is_reset", "seg", "pos0", "seg_len", "day_len").sort("agent", "t_first", "turn_id"))
    calls = calls.with_columns(pl.int_range(pl.len()).over("agent", "pt_date").alias("seq"))
    rst = pl.col("reset_consol") | pl.col("reset_session") | pl.col("first_of_day") | (pl.col("seq") == 0)
    calls = calls.with_columns(rst.alias("is_reset"))
    calls = calls.with_columns(pl.col("is_reset").cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("seg"))
    calls = calls.with_columns(pl.int_range(pl.len()).over("agent", "pt_date", "seg").alias("pos0"),
                               pl.len().over("agent", "pt_date", "seg").alias("seg_len"))
    calls = calls.with_row_index("g").with_columns(pl.col("g").cast(pl.Int64))
    refuse_holdout(calls["pt_date"].unique().to_list(), "calls")
    n = calls.height
    lt = pl.read_parquet(SH / "context_ledger_turns.parquet", columns=["turn_id", "n_agent", "n_human"])
    calls = calls.join(lt, on="turn_id", how="left", maintain_order="left")
    log("calls", n)
    agent = calls["agent"].to_numpy()
    day = calls["pt_date"].to_numpy()
    seq = calls["seq"].to_numpy()
    first_g = (np.arange(n) - seq).astype(np.int64)            # g of the agent-day's first call
    items = (calls["n_agent"].fill_null(0) + calls["n_human"].fill_null(0)).to_numpy()
    search = (calls["kind"].cast(pl.Utf8) == "search").to_numpy()
    r3 = ((calls["regime"] == "III") & (calls["ctx_mode"].cast(pl.Utf8) == "cu")).to_numpy()

    # ---- command rows -> calls
    to = pl.read_parquet(ROOT / "data/processed/behavior_states/turn_outcomes.parquet",
                         columns=["t", "agent", "act", "cmd", "commit_ok", "push_ok", "file_write", "api_write", "deploy"])
    to = to.filter(pl.col("t") >= dt.datetime(2026, 2, 9, 8, tzinfo=dt.timezone.utc)).sort("t")
    keys = calls.select("g", "agent", "t_first", "t_log").sort("t_first")
    to = to.join_asof(keys, left_on="t", right_on="t_first", by="agent", strategy="backward", check_sortedness=False)
    to = to.filter(pl.col("g").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=1)))
    log("command rows mapped", to.height)
    write = np.zeros(n, bool)
    wr = to.filter(pl.col("commit_ok") | pl.col("push_ok") | pl.col("file_write") | pl.col("api_write") | pl.col("deploy"))
    write[wr["g"].to_numpy()] = True
    n_read_rows = np.zeros(n, np.int32)
    n_rows = np.zeros(n, np.int32)
    notes = np.zeros(n, bool)
    obj_lists: list[list[int]] = [[] for _ in range(n)]
    term_lists: list[list[np.ndarray]] = [[] for _ in range(n)]
    gs, acts, cmds = to["g"].to_numpy(), to["act"].cast(pl.Utf8).to_list(), to["cmd"].to_list()
    for i, (g, a, c) in enumerate(zip(gs, acts, cmds)):
        n_rows[g] += 1
        if a == "bash":
            rd, nt, ob = classify(c or "")
            n_read_rows[g] += rd
            notes[g] |= nt
            obj_lists[g].extend(ob)
        else:
            _, _, ob = classify(c or "")       # typed text: objects only (never a read)
            obj_lists[g].extend(ob)
        if r3[g]:
            term_lists[g].append(hset(c or ""))
        if i % 200000 == 0:
            log("  rows", i)
    read = (n_read_rows > 0) & (n_read_rows == n_rows) & ~write
    notes &= read
    objs = [set(o) for o in obj_lists]
    del obj_lists
    log("classified; read calls", int(read.sum()), "notes reads", int(notes.sum()))

    # classifier agreement with H44 (read-only data check, not used in any statistic)
    chk = {}
    h44p = ROOT / "data/processed/H44-erasure-reacquisition-thrash/calls.parquet"
    if h44p.exists():
        h = pl.read_parquet(h44p)
        cat_col = next((c for c in ("cat", "category", "call_cat") if c in h.columns), None)
        if cat_col and "turn_id" in h.columns:
            mine = pl.DataFrame({"turn_id": calls["turn_id"], "read": read, "notes": notes})
            # H44 integer codes follow its priority list: 0 write, 1 talk, 2 room read, 3 notes read, 4 local read,
            # 5 remote read, 6 run, 7 look, 8 GUI type, 9 GUI, 10 monitor, 11 setup, 12 idle, 13 other
            j = h.select("turn_id", pl.col(cat_col).cast(pl.Int64).alias("c")).join(mine, on="turn_id", how="inner")
            j = j.with_columns(pl.col("c").is_in([3, 4, 5]).alias("h44_read"))
            tab = j.group_by("c").agg(pl.len(), pl.col("read").mean().alias("share_read_r2")).sort("len", descending=True)
            chk = {"n": j.height, "agree": float((j["read"] == j["h44_read"]).mean()),
                   "p_read_given_h44read": float(j.filter(pl.col("h44_read"))["read"].mean()),
                   "p_h44read_given_read": float(j.filter(pl.col("read"))["h44_read"].mean()),
                   "by_h44_category": tab.rows()}
        else:
            chk = {"note": f"H44 calls.parquet has no category column ({h.columns[:12]})"}
    (OUT / "classifier_check.json").write_text(json.dumps(chk, indent=1, default=str))
    log("classifier check", {k: v for k, v in chk.items() if k != "by_h44_category"})

    # ---- repos: work commits and artifact touches
    ids, amap = CP.repo_map()
    wc = CP.work_commits(ids)
    keys_log = calls.select("g", "agent", "t_log").sort("t_log")
    wm = wc.join_asof(keys_log, left_on="t", right_on="t_log", by="agent", strategy="forward", tolerance="10m",
                      check_sortedness=False).drop_nulls("g")
    n_work = np.zeros(n, np.int32)
    np.add.at(n_work, wm["g"].to_numpy(), 1)
    cs = np.concatenate([[0], np.cumsum(n_work)])
    am = pl.read_parquet(SH / "artifact_mentions.parquet", columns=["artifact", "t", "agent", "source"])
    act = (am.filter(pl.col("source") == "action").join(amap, on="artifact", how="inner").select("t", "agent", "rid")
           .sort("t").join_asof(keys.sort("t_first"), left_on="t", right_on="t_first", by="agent", strategy="backward",
                                check_sortedness=False))
    act = act.filter(pl.col("g").is_not_null() & (pl.col("t") <= pl.col("t_log") + pl.duration(seconds=1)))
    touched: list[set] = [set() for _ in range(n)]
    for g, r in zip(act["g"].to_list(), act["rid"].to_list()):
        touched[g].add(r)
    it = CP.admit_aux(am.filter(pl.col("source") == "intention"), False, None)
    it = (it.join(amap, on="artifact", how="inner").select(pl.col("t").alias("t_int"), "agent", pl.col("rid").alias("S_M"))
          .unique(["agent", "t_int"], keep="first", maintain_order=True).sort("t_int"))
    log("repos mapped: work commits", wm.height, "touch rows", act.height)

    # ---- events F / P
    c = calls
    isF = r3 & c["reset_forced"].to_numpy()
    isP = r3 & (c["pos0"].to_numpy() == 20) & (c["seg_len"].to_numpy() >= 40)
    ev = (c.filter(pl.Series(isF | isP)).select("g", "turn_id", "agent", "pt_date", "goal_no", "t_call", "t_first",
                                                "pos0", "seg_len")
          .with_columns(pl.when(pl.Series(isF[isF | isP])).then(pl.lit("F")).otherwise(pl.lit("P")).alias("etype")))
    ev = ev.sort("t_call").join_asof(wc.select(pl.col("t").alias("t_c"), "agent", pl.col("rid").alias("A_prev")),
                                     left_on="t_call", right_on="t_c", by="agent", strategy="backward", tolerance="7d",
                                     check_sortedness=False)
    ev = ev.join_asof(it, left_on="t_call", right_on="t_int", by="agent", strategy="backward", tolerance="24h",
                      check_sortedness=False)
    ev = ev.with_columns(pl.col("A_prev").fill_null(-1), pl.col("S_M").fill_null(-1)).drop("t_c", "t_int").sort("g")
    # own commits per agent for the trail
    wca = {a: (sub["t"].to_numpy().astype("datetime64[us]").astype(np.int64), sub["rid"].to_numpy(),
               sub["pt_date"].to_numpy()) for (a,), sub in wc.group_by(["agent"])}
    tfirst = c["t_first"].to_numpy().astype("datetime64[us]").astype(np.int64)
    DAY_US = 86_400_000_000
    rows = {k: [] for k in ("n_win", "V20", "V3", "V6", "V_pre", "W10", "first_write", "rs5", "touch5", "touchA5",
                            "first_read", "L", "M", "Gp", "S_C", "L35", "M35", "trail24", "trail_days7", "n_pre_obj")}
    for gi, p0, sl, a_prev in zip(ev["g"].to_numpy(), ev["pos0"].to_numpy(), ev["seg_len"].to_numpy(),
                                  ev["A_prev"].to_numpy()):
        nw = int(min(WIN, sl - p0))
        rows["n_win"].append(nw)
        rows["V20"].append(float(cs[gi + nw] - cs[gi]) * WIN / nw if nw > 0 else np.nan)
        rows["V3"].append(float(cs[gi + nw] - cs[gi + 2]) * 18 / (nw - 2) if nw > 2 else np.nan)
        rows["V6"].append(float(cs[gi + nw] - cs[gi + 5]) * 15 / (nw - 5) if nw > 5 else np.nan)
        lo = max(gi - PRE_V, first_g[gi])
        rows["V_pre"].append(float(cs[gi] - cs[lo]))
        w10 = write[gi:gi + min(10, nw)]
        rows["W10"].append(float(w10.mean()) if len(w10) else np.nan)
        fw = np.flatnonzero(write[gi:gi + nw])
        rows["first_write"].append(int(fw[0]) + 1 if len(fw) else nw + 1)
        e5 = gi + min(5, nw)
        rs = read[gi:e5] | search[gi:e5]
        rows["rs5"].append(float(rs.mean()) if len(rs) else np.nan)
        fr = np.flatnonzero(rs)
        rows["first_read"].append(int(fr[0]) + 1 if len(fr) else 6)
        pre_o = set().union(*objs[max(gi - PRE_OBJ, first_g[gi]):gi]) if gi > first_g[gi] else set()
        pre_l = set().union(*objs[max(gi - PRE_L, first_g[gi]):gi]) if gi > first_g[gi] else set()
        rows["n_pre_obj"].append(len(pre_o))
        rows["touch5"].append(bool(any(read[k] and (objs[k] & pre_o) for k in range(gi, e5))))
        rows["touchA5"].append(bool(a_prev >= 0 and any(a_prev in touched[k] for k in range(gi, e5))))
        e2 = gi + min(2, nw)
        rows["L"].append(bool(any(read[k] and (objs[k] & pre_l) for k in range(gi, e2))))
        rows["M"].append(bool(items[gi:e2].sum() > 0))
        rows["Gp"].append(bool((notes[gi:e2] | search[gi:e2]).any()))
        rows["L35"].append(bool(any(read[k] and (objs[k] & pre_l) for k in range(e2, e5))))
        rows["M35"].append(bool(items[e2:e5].sum() > 0))
        cnt = Counter()
        for k in range(max(gi - PRE_L, first_g[gi]), gi):
            cnt.update(touched[k])
        rows["S_C"].append(min((r for r, v in cnt.items() if v == max(cnt.values())), default=-1) if cnt else -1)
        # trail: own commits to A_prev in the 24 h before the event, older than call -40 (or the day's first call)
        t_ev = tfirst[gi]
        cut = tfirst[max(gi - 40, first_g[gi])]
        a = int(agent[gi])
        if a_prev >= 0 and a in wca:
            tt, rr, dd = wca[a]
            m = (rr == a_prev)
            rows["trail24"].append(int(((tt >= t_ev - DAY_US) & (tt < cut) & m).sum()))
            m7 = m & (tt >= t_ev - 7 * DAY_US) & (dd < day[gi])
            rows["trail_days7"].append(int(len(np.unique(dd[m7]))))
        else:
            rows["trail24"].append(0)
            rows["trail_days7"].append(0)
    ev = ev.with_columns(**{k: pl.Series(v) for k, v in rows.items()})
    ev = ev.with_columns(((pl.col("S_M") == pl.col("S_C")) & (pl.col("S_C") >= 0)).alias("Gn"),
                         pl.format("G{}", pl.col("goal_no").cast(pl.Utf8).str.zfill(2)).alias("period"),
                         pl.format("{}|{}", "agent", "pt_date").alias("cluster"))
    ev = ev.with_columns(pl.format("{}|{}", "agent", "period").alias("stratum"))
    refuse_holdout(ev["pt_date"].unique().to_list(), "events")
    ev.write_parquet(OUT / "events.parquet", compression="zstd")
    log("events", ev.group_by("etype").len().rows())

    # ---- R1c: consolidation-opened segments (read-or-search share of calls 1-5), regime III
    segstart = r3 & c["reset_consol"].to_numpy() & (c["pos0"].to_numpy() == 0)
    sg = c.filter(pl.Series(segstart)).select("g", "agent", "pt_date", "goal_no", "t_first", "seg_len",
                                              "reset_forced")
    rs5 = []
    for gi, sl in zip(sg["g"].to_numpy(), sg["seg_len"].to_numpy()):
        e5 = gi + min(5, int(sl))
        x = read[gi:e5] | search[gi:e5]
        rs5.append(float(x.mean()))
    sg = sg.with_columns(pl.Series("rs5", rs5), pl.format("G{}", pl.col("goal_no").cast(pl.Utf8).str.zfill(2)).alias("period"))
    sg.write_parquet(OUT / "segs.parquet", compression="zstd")
    # per agent-day read-or-search share (newcomers)
    ad = (pl.DataFrame({"agent": agent, "pt_date": day, "rs": (read | search).astype(np.int8), "r3": r3})
          .filter(pl.col("r3")).group_by("agent", "pt_date").agg(pl.len().alias("n_calls"), pl.col("rs").mean().alias("rs_share")))
    ad.write_parquet(OUT / "newcomer_days.parquet", compression="zstd")
    log("segments", sg.height, "agent-days", ad.height)

    # ---- R3: notes, windows and term sets
    int_t = pl.read_parquet(SH / "intentions.parquet").join(pl.read_parquet(SH / "intentions_text.parquet"),
                                                             on="event_index")
    int_t = int_t.filter((pl.col("source") == "CONSOLIDATE") & (pl.col("t") >= R3_START))
    int_t = CP.admit_aux(int_t, False, None)
    int_t = int_t.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8)
                               .alias("pt_date")).sort("t")
    # the first call after the note (same agent-day) opens the post segment
    nk = c.filter(pl.Series(r3)).select("g", "agent", "t_first", "pt_date").sort("t_first")
    int_t = int_t.join_asof(nk.rename({"pt_date": "c_date"}), left_on="t", right_on="t_first", by="agent",
                            strategy="forward", tolerance="30m", check_sortedness=False)
    int_t = int_t.filter(pl.col("g").is_not_null() & (pl.col("c_date") == pl.col("pt_date")))
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
    int_t = int_t.join(cal, on="pt_date", how="left").filter(pl.col("goal_no").is_not_null())
    log("notes with a post call", int_t.height)
    # chat terms per agent
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "speaker_kind", "agent"])
    cc = cc.filter((pl.col("speaker_kind") == "agent") & (pl.col("t") >= R3_START))
    ct = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"])
    cc = cc.join(ct, on="message_id", how="inner").sort("t")
    chat_by_agent = {}
    for (a,), sub in cc.group_by(["agent"]):
        sub = sub.sort("t")
        chat_by_agent[int(a)] = (sub["t"].to_numpy().astype("datetime64[us]").astype(np.int64),
                                 [hset(x) for x in sub["text"].to_list()])
    del cc, ct
    tlog = c["t_log"].to_numpy().astype("datetime64[us]").astype(np.int64)
    pos0 = c["pos0"].to_numpy()
    segl = c["seg_len"].to_numpy()
    seg = c["seg"].to_numpy()
    note_terms = [hset(x) for x in int_t["goal_text"].to_list()]
    goal = int_t["goal_no"].to_numpy()
    vocab = {}
    for gno, tset in zip(goal, note_terms):
        vocab.setdefault(int(gno), set()).update(tset.tolist())
    vocab = {k: np.array(sorted(v), dtype=np.int64) for k, v in vocab.items()}

    def window_terms(g0: int, g1: int, voc: np.ndarray) -> np.ndarray:
        parts = [x for k in range(g0, g1) for x in term_lists[k]]
        if not parts:
            return np.zeros(0, np.int64)
        u = np.unique(np.concatenate(parts))
        return u[np.isin(u, voc, assume_unique=True)]

    def chat_terms(a: int, t0: int, t1: int, voc: np.ndarray) -> np.ndarray:
        if a not in chat_by_agent:
            return np.zeros(0, np.int64)
        tt, hs = chat_by_agent[a]
        i0, i1 = np.searchsorted(tt, t0), np.searchsorted(tt, t1, side="right")
        if i1 <= i0:
            return np.zeros(0, np.int64)
        u = np.unique(np.concatenate(hs[i0:i1]))
        return u[np.isin(u, voc, assume_unique=True)]

    rec = {k: [] for k in ("post", "post10", "post31", "pre", "chat_post", "chat_pre", "n_post", "n_pre", "post_forced",
                           "pre_forced")}
    for gi, gno in zip(int_t["g"].to_numpy(), goal):
        voc = vocab[int(gno)]
        a = int(agent[gi])
        # post segment: the segment that call gi opens (gi should be its first call)
        p_end = gi + int(min(40, segl[gi] - pos0[gi]))
        rec["post"].append(window_terms(gi, p_end, voc))
        rec["post10"].append(window_terms(gi, min(gi + 10, p_end), voc))
        rec["post31"].append(window_terms(gi + 30, p_end, voc) if p_end > gi + 30 else np.zeros(0, np.int64))
        rec["n_post"].append(p_end - gi)
        rec["post_forced"].append(bool(c["reset_forced"][int(gi)]))
        # pre segment: the calls of the same agent-day before gi, back to the previous segment start (<= 40)
        if gi > first_g[gi] and seg[gi - 1] == seg[gi - 1] and agent[gi - 1] == a and day[gi - 1] == day[gi]:
            q = gi - 1
            q0 = max(q - int(pos0[q]), q - 39)
            rec["pre"].append(window_terms(q0, gi, voc))
            rec["n_pre"].append(gi - q0)
            rec["chat_pre"].append(chat_terms(a, int(tfirst[q0]), int(tlog[gi - 1]), voc))
            rec["pre_forced"].append(int(segl[q]) >= 40)
        else:
            rec["pre"].append(np.zeros(0, np.int64))
            rec["n_pre"].append(0)
            rec["chat_pre"].append(np.zeros(0, np.int64))
            rec["pre_forced"].append(False)
        rec["chat_post"].append(chat_terms(a, int(tfirst[gi]), int(tlog[p_end - 1]), voc))
    notes_df = int_t.select("event_index", "agent", "t", "pt_date", "goal_no", "g").with_columns(
        pl.Series("terms", [x.tolist() for x in note_terms], dtype=pl.List(pl.Int64)),
        pl.format("G{}", pl.col("goal_no").cast(pl.Utf8).str.zfill(2)).alias("period"),
        **{k: (pl.Series(k, [x.tolist() for x in v], dtype=pl.List(pl.Int64)) if isinstance(v[0], np.ndarray)
               else pl.Series(k, v)) for k, v in rec.items()})
    refuse_holdout(notes_df["pt_date"].unique().to_list(), "notes")
    notes_df.write_parquet(OUT / "notes.parquet", compression="zstd")
    log("notes", notes_df.height, "median terms", float(notes_df["terms"].list.len().median()),
        "median post terms", float(notes_df["post"].list.len().median()))

    prov_p = OUT / "_provenance.json"
    prov = json.loads(prov_p.read_text()) if prov_p.exists() else {}
    prov["build_r2"] = {"built_by": "hypotheses/H15-semantic-information-scrambles/scheme/build_r2.py",
                        "git_commit": git_commit(),
                        "inputs": [{"source": "ai-village", "revision": REVISION,
                                    "tables": ["context_ledger_turns", "turn_outcomes", "work_commits", "work_repos",
                                               "artifacts", "artifact_mentions", "intentions", "intentions_text",
                                               "chat_core", "chat_text", "calendar", "period_units"]}],
                        "params": {"WIN": WIN, "MIN_WIN": MIN_WIN, "PRE_V": PRE_V, "PRE_OBJ": PRE_OBJ, "PRE_L": PRE_L,
                                   "shared_code": ["infra/shared/channel_pointers.py (load_calls, repo_map, work_commits,"
                                                   " admit_aux)"]},
                        "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_p.write_text(json.dumps(prov, indent=1))
    log("done")


if __name__ == "__main__":
    main()
