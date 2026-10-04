"""Collect the lab's state from the repo for the dashboard.

Reads only cards, folder structure, file metadata, provenance JSON, LOG.md, git, ps, the Claude Code
subagent transcripts under ~/.claude/projects/<project>/, and two numeric shared tables for the phase diagram
(per_period_estimates.parquet, period_units.parquet). It never opens the gated text tables in data/.
Everything is cached with short TTLs so the page can poll every few seconds.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HYP = ROOT / "hypotheses"
PROC = ROOT / "data/processed"
CLAUDE_PROJECT = Path.home() / ".claude/projects" / ("-" + str(ROOT).strip("/").replace("/", "-"))

PERIOD_RE = re.compile(r"^(G(\d{2})([a-z]?)|NE(\d{2}))(-.*)?$")
VERDICTS = ("supported", "failed", "mixed", "descriptive", "pending", "n/a")
AXES = "ABCDEFGHI"
STAGES = ["card", "predictions", "synthetic", "periods", "scorecard", "confirm script", "holdout run"]

_cache: dict = {}


def cached(key, ttl, fn):
    hit = _cache.get(key)
    now = time.time()
    if hit and now - hit[0] < ttl:
        return hit[1]
    val = fn()
    _cache[key] = (now, val)
    return val


def iso(ts: float | None):
    return datetime.fromtimestamp(ts, timezone.utc).isoformat() if ts else None


def dir_stats(path: Path):
    """(total bytes, newest mtime, n files) for a directory tree."""
    total, newest, n = 0, 0.0, 0
    if not path.exists():
        return 0, None, 0
    for dp, dns, fns in os.walk(path):
        dns[:] = [d for d in dns if d not in (".git", "__pycache__")]
        for f in fns:
            try:
                st = os.stat(os.path.join(dp, f))
            except OSError:
                continue
            total += st.st_size
            n += 1
            newest = max(newest, st.st_mtime)
    return total, (newest or None), n


def field(text: str, name: str) -> str:
    m = re.search(rf"^\*\*{re.escape(name)}:\*\*\s*(.+)$", text, re.M)
    return m.group(1).strip() if m else ""


def sections(text: str) -> dict[str, str]:
    out, cur, buf = {}, "_head", []
    for line in text.splitlines():
        if line.startswith("## "):
            out[cur] = "\n".join(buf)
            cur, buf = line[3:].strip(), []
        else:
            buf.append(line)
    out[cur] = "\n".join(buf)
    return out


def strip_md(s: str) -> str:
    return re.sub(r"\*\*|__|`", "", s).strip()


SYNONYMS = (("not supported", "failed"), ("unsupported", "failed"), ("falsified", "failed"), ("refuted", "failed"),
            ("fail", "failed"), ("inconclusive", "mixed"), ("partial", "mixed"), ("partly", "mixed"),
            ("confirmed", "supported"), ("passed", "supported"), ("pass", "supported"), ("na", "n/a"), ("not applicable", "n/a"))


def verdict_key(v: str) -> str:
    v = collect_clean(v)
    for k in VERDICTS:
        if v.startswith(k):
            return k
    for syn, k in SYNONYMS:
        if v.startswith(syn):
            return k
    parts = re.findall(r"\bp\d+[a-z]?\s*:?\s*([a-z/ ]+?)(?:\(|;|,|$)", v)  # "P1 supported; P2 failed" → combine
    if parts:
        ks = {verdict_key(x.strip()) for x in parts} - {"other"}
        if ks == {"supported"}:
            return "supported"
        if ks == {"failed"}:
            return "failed"
        if ks:
            return "mixed"
    return "pending" if not v else "other"


def collect_clean(v: str) -> str:
    return re.sub(r"^[\W_]+", "", v.lower().replace("**", "")).strip()


# --------------------------------------------------------------------------------------------- hypotheses

def parse_scorecard(sec: str) -> dict:
    scores = {}
    for line in sec.splitlines():
        m = re.match(r"^\|\s*([A-I])\b[^|]*\|[^|]*\|([^|]*)\|", line)
        if m:
            d = re.search(r"[0-2]", m.group(2))
            scores[m.group(1)] = int(d.group()) if d else None
    return scores


def level(sc: dict, confirmed: bool) -> str:
    g = lambda k: sc.get(k) if sc.get(k) is not None else -1
    if (g("A") == 2 and g("B") >= 1 and g("C") == 2 and g("D") == 2 and g("F") >= 1 and g("H") >= 1
            and (g("E") == 2 or g("G") == 2) and confirmed):
        if g("E") == 2 and g("F") == 2 and g("H") == 2 and g("I") == 2:
            return "faithful"
        return "supported"
    if g("C") == 2 and g("D") >= 1:
        return "descriptive"
    return "hypothesis"


PERIOD_SUB = "goalperiod-subhypotheses"


def period_folders(hdir: Path) -> list[dict]:
    out = []
    cands = sorted((hdir / PERIOD_SUB).iterdir()) if (hdir / PERIOD_SUB).is_dir() else []
    cands += [d for d in sorted(hdir.iterdir()) if not (hdir / PERIOD_SUB / d.name).exists()]  # stragglers at the old place
    for d in cands:
        if d.is_dir() and PERIOD_RE.match(d.name) and (d / "README.md").exists():
            t = (d / "README.md").read_text(errors="replace")
            v1b = field(t, "Verdict (1b)")
            v, role = v1b or field(t, "Verdict"), field(t, "Role")
            out.append({"period": d.name, "verdict": verdict_key(v), "verdict_text": strip_md(v)[:240],
                        "round": "1b" if v1b else "1",
                        "scope": strip_md(role + " " + field(t, "Period")),
                        "role": "confirmatory" if role.lower().startswith("confirm") else "exploratory",
                        "path": str((d / "README.md").relative_to(ROOT)),
                        "mtime": iso((d / "README.md").stat().st_mtime)})
    return out


MODEL_RE = re.compile(r"physics-models/(\d{2})-[a-z0-9-]+")


def card_models(text: str, meta: dict) -> list[dict]:
    """Physics models a hypothesis uses. meta.json `models` (RUBRIC.md) wins; otherwise a fallback from the card:
    models on the From/Models line or in the Model section are 'primary', other mentions 'mentioned'."""
    if isinstance(meta.get("models"), list) and meta["models"]:
        out = []
        for m in meta["models"]:
            mid = str(m.get("model", ""))[:2]
            if mid.isdigit():
                out.append({"model": mid, "role": m.get("role", "primary"), "outcome": m.get("outcome", "untested"),
                            "note": m.get("note", ""), "source": "meta"})
        return out
    head = "\n".join(l for l in text.splitlines()[:12] if "From:" in l or "Models:" in l)
    msec = sections(text).get("Model", "")
    prim = set(MODEL_RE.findall(head)) | set(MODEL_RE.findall(msec))
    allm = set(MODEL_RE.findall(text))
    return ([{"model": m, "role": "primary", "outcome": "untested", "note": "", "source": "card"} for m in sorted(prim)] +
            [{"model": m, "role": "mentioned", "outcome": "untested", "note": "", "source": "card"} for m in sorted(allm - prim)])


def physics_models() -> list[dict]:
    """Model index from physics-models/README.md (number, name, swarm variable, signature behaviour)."""
    out = []
    readme = ROOT / "physics-models/README.md"
    if not readme.exists():
        return out
    for line in readme.read_text(errors="replace").splitlines():
        m = re.match(r"\|\s*\[(\d{2})\]\(([^)]+)\)\s*\|\s*([^|]+)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|", line)
        if m:
            out.append({"id": m.group(1), "path": "physics-models/" + m.group(2).strip("/") + "/README.md",
                        "name": m.group(3).strip(), "fields": m.group(4).strip(), "variable": m.group(5).strip(),
                        "signature": m.group(6).strip()})
    return out


VET = ROOT / "hypotheses/hypohypotheses/vetting.json"
VET_LOG = ROOT / "hypotheses/hypohypotheses/vetting_decisions.jsonl"
VET_DECISIONS = {"approved", "declined", "later", "undo"}


def vetting() -> dict:
    try:
        v = json.loads(VET.read_text()) if VET.exists() else {"items": []}
    except ValueError:
        v = {"items": []}
    return v


def record_vet(hh: str, decision: str, note: str = "") -> dict:
    """Record a vetting click: update vetting.json and append to vetting_decisions.jsonl (the coordinator watches it)."""
    if decision not in VET_DECISIONS:
        return {"error": "bad decision"}
    v = vetting()
    item = next((x for x in v.get("items", []) if x.get("id") == hh), None)
    if item is None:
        return {"error": "unknown HH"}
    now = iso(time.time())
    if decision == "undo":
        item.pop("decision", None); item.pop("decided_at", None); item.pop("vet_note", None)
    else:
        item["decision"], item["decided_at"] = decision, now
        if note:
            item["vet_note"] = note
    VET.write_text(json.dumps(v, indent=1, ensure_ascii=False) + "\n")
    with VET_LOG.open("a") as f:
        f.write(json.dumps({"id": hh, "decision": decision, "note": note, "at": now}, ensure_ascii=False) + "\n")
    return {"ok": True, "id": hh, "decision": decision}


def constants() -> dict:
    p = ROOT / "interpretation/swarm-constants.json"
    try:
        return json.loads(p.read_text()) if p.exists() else {}
    except ValueError:
        return {}


def hypothesis(hdir: Path) -> dict:
    card = hdir / "README.md"
    text = card.read_text(errors="replace") if card.exists() else ""
    sec = sections(text)
    title = text.splitlines()[0].lstrip("# ").strip() if text else hdir.name
    hid = hdir.name.split("-")[0]
    status = strip_md(field(text, "Status"))
    sc = parse_scorecard(sec.get("Faithfulness scorecard", ""))
    periods = period_folders(hdir)
    counts = {k: 0 for k in VERDICTS}
    for p in periods:
        counts[p["verdict"]] = counts.get(p["verdict"], 0) + 1
    conf = [p for p in periods if p["role"] == "confirmatory"]
    conf_run = [p for p in conf if p["verdict"] not in ("pending", "other")]
    data_dir = PROC / hdir.name
    data_conf = [p.name for p in data_dir.glob("confirm*") if "dry" not in p.name.lower()] if data_dir.exists() else []
    analysis = list((hdir / "analysis").glob("*.py")) if (hdir / "analysis").exists() else []
    confirm_scripts = [p.name for p in analysis if p.name.startswith("confirm")]

    pred_body = "\n".join(l for l in sec.get("Prediction", "").splitlines()
                          if l.strip() and not l.strip().startswith(("*Write", "<")))
    q_body = sec.get("Question", "").strip()
    stage = {
        "card": 1.0 if q_body and not q_body.startswith("<") else 0.0,
        "predictions": 1.0 if len(pred_body) > 150 else 0.0,
        "synthetic": 1.0 if (sc.get("F") is not None or any(re.search(r"synth|valid|calib|harness", p.name) for p in analysis)) else 0.0,
        "periods": (sum(1 for p in periods if p["verdict"] not in ("pending", "other")) / len(periods)) if periods else 0.0,
        "scorecard": sum(1 for a in AXES if sc.get(a) is not None) / 9,
        "confirm script": 1.0 if confirm_scripts else 0.0,
        "holdout run": 1.0 if (conf_run or data_conf) else 0.0,
    }
    meta = {}
    mp = hdir / "summary/meta.json"
    if mp.exists():
        try:
            meta = json.loads(mp.read_text())
        except ValueError:
            meta = {}
    rating = {k: meta.get(k) for k in ("complete", "faithfulness", "usefulness", "one_line", "rated_by", "updated")}
    rating["rationale"] = meta.get("rationale", {})
    rating["v2"] = meta.get("v2")  # scoring v2 (writeup/scoring/scoring-v2.pdf): claim, credence, mechanism, fragility, V, EU, S
    models = card_models(text, meta)
    size, newest, nfiles = dir_stats(hdir)
    dsize, dnewest, _ = dir_stats(data_dir)
    last = max(x for x in (newest, dnewest, 0) if x is not None) or None
    return {
        "id": hid, "slug": hdir.name, "title": title.split(":", 1)[-1].strip(), "status": status,
        "card": str(card.relative_to(ROOT)) if card.exists() else None,
        "scores": {a: sc.get(a) for a in AXES}, "level": level(sc, bool(conf_run)),
        "stages": stage, "progress": round(100 * sum(stage.values()) / len(stage)),
        "periods": periods, "verdicts": counts,
        "confirm_scripts": confirm_scripts, "confirm_runs": [p["period"] for p in conf_run] or data_conf,
        "confirm_verdicts": [{"period": p["period"], "verdict": p["verdict"], "text": p["verdict_text"]} for p in conf_run],
        "data_bytes": dsize, "files": nfiles, "last_activity": iso(last),
        "parked": "parked" in status.lower(), "rating": rating, "models": models,
        "summary_pdf": str((hdir / "summary/summary.pdf").relative_to(ROOT)) if (hdir / "summary/summary.pdf").exists() else None,
    }


def hypotheses() -> list[dict]:
    hs = [hypothesis(d) for d in sorted(HYP.iterdir()) if d.is_dir() and re.match(r"^H\d{2}-", d.name)]
    return hs


# --------------------------------------------------------------------------------------------- agents

def _agent(meta_path: Path) -> dict | None:
    tr = meta_path.with_name(meta_path.name.replace(".meta.json", ".jsonl"))
    try:
        meta = json.loads(meta_path.read_text())
        st = tr.stat()
    except (OSError, ValueError):
        return None
    key = ("agent", str(tr), st.st_size, st.st_mtime)
    hit = _cache.get(key)
    if hit:
        return hit[1]
    raw = tr.read_bytes()
    tail = raw[-400_000:].decode("utf-8", "replace")
    hb = max(tail.rfind('"name":"SubagentHandback"'), tail.rfind('"name": "SubagentHandback"'))
    # a resumed agent keeps working after an earlier hand-back: only count it finished if nothing follows
    finished = hb >= 0 and tail[hb:].count('"type":"tool_use"') == 0
    tool_uses = raw.count(b'"type":"tool_use"')
    ts = re.findall(r'"timestamp":"([^"]+)"', raw[:200_000].decode("utf-8", "replace"))
    started = ts[0] if ts else iso(getattr(st, "st_birthtime", st.st_ctime))
    last_tools = []
    for line in tail.splitlines()[-60:]:
        try:
            j = json.loads(line)
        except ValueError:
            continue
        m = j.get("message") or {}
        if j.get("type") == "assistant" and isinstance(m.get("content"), list):
            for c in m["content"]:
                if c.get("type") == "tool_use":
                    inp = c.get("input") or {}
                    last_tools.append({"tool": c.get("name"), "what": str(inp.get("description") or inp.get("file_path") or inp.get("command") or "")[:140],
                                       "t": j.get("timestamp")})
    desc = meta.get("description", "")
    m = re.search(r"\bH(\d{2})\b", desc)
    age = time.time() - st.st_mtime
    state = "finished" if finished else ("running" if age < 15 * 60 else "stalled")
    out = {"id": tr.stem.replace("agent-", ""), "description": desc, "hypothesis": f"H{m.group(1)}" if m else None,
           "session": tr.parent.parent.name[:8], "state": state, "started": started, "last_activity": iso(st.st_mtime),
           "tool_uses": tool_uses, "bytes": st.st_size, "last_tools": last_tools[-5:]}
    _cache[key] = (time.time(), out)
    return out


def agents(hours: float = 48) -> list[dict]:
    if not CLAUDE_PROJECT.exists():
        return []
    cutoff = time.time() - hours * 3600
    out = []
    for meta in CLAUDE_PROJECT.glob("*/subagents/*.meta.json"):
        tr = meta.with_name(meta.name.replace(".meta.json", ".jsonl"))
        if tr.exists() and tr.stat().st_mtime >= cutoff:
            a = _agent(meta)
            if a:
                out.append(a)
    order = {"running": 0, "stalled": 1, "finished": 2}
    return sorted(out, key=lambda a: (order[a["state"]], a["last_activity"] or ""), reverse=False)


def agent_report(agent_id: str) -> dict:
    """The agent's hand-back report (or its latest assistant text if still running)."""
    hits = list(CLAUDE_PROJECT.glob(f"*/subagents/agent-{re.sub(r'[^a-z0-9]', '', agent_id)}.jsonl"))
    if not hits:
        return {"error": "not found"}
    report, last_text = None, None
    for line in hits[0].read_text(errors="replace").splitlines():
        try:
            j = json.loads(line)
        except ValueError:
            continue
        m = j.get("message") or {}
        if j.get("type") == "assistant" and isinstance(m.get("content"), list):
            for c in m["content"]:
                if c.get("type") == "tool_use" and c.get("name") == "SubagentHandback":
                    inp = c.get("input") or {}
                    report = next((v for v in inp.values() if isinstance(v, str) and len(v) > 40), json.dumps(inp))
                elif c.get("type") == "text" and c.get("text", "").strip():
                    last_text = c["text"]
    meta = hits[0].with_name(hits[0].name.replace(".jsonl", ".meta.json"))
    desc = json.loads(meta.read_text()).get("description", "") if meta.exists() else ""
    return {"id": agent_id, "description": desc, "report": report, "latest_text": None if report else last_text}


# --------------------------------------------------------------------------------------------- pipelines

def _rows(path: Path):
    try:
        if path.suffix == ".parquet":
            import pyarrow.parquet as pq
            return pq.read_metadata(path).num_rows
        if path.suffix == ".npy":
            import numpy as np
            with open(path, "rb") as f:
                v = np.lib.format.read_magic(f)
                shape, _, _ = np.lib.format._read_array_header(f, v)
            return "×".join(str(s) for s in shape)
    except Exception:
        return None
    return None


def _script_for(name: str, built_by: str) -> Path | None:
    for cand in (ROOT / built_by, ROOT / "infra/shared" / f"{name.split(':')[0]}.py"):
        if cand.exists():
            return cand
    hits = list((ROOT / "infra").rglob(f"{name.split(':')[0]}.py"))
    return hits[0] if hits else None


def pipelines() -> dict:
    shared = PROC / "shared"
    tables = []
    for p in sorted(list(shared.glob("*.parquet")) + list(shared.glob("embeddings/*"))):
        if p.is_file() and p.suffix in (".parquet", ".npy", ".npz"):
            st = p.stat()
            tables.append({"name": str(p.relative_to(shared)), "bytes": st.st_size, "mtime": iso(st.st_mtime),
                           "rows": _rows(p) if p.suffix != ".npz" else None})
    prov = []
    pf = shared / "_provenance.json"
    if pf.exists():
        for name, e in json.loads(pf.read_text()).items():
            script = _script_for(name, e.get("built_by", ""))
            built = e.get("built_at")
            stale = None
            if script and built:
                try:
                    stale = script.stat().st_mtime > datetime.fromisoformat(built).timestamp() + 5
                except ValueError:
                    pass
            prov.append({"name": name, "script": str(script.relative_to(ROOT)) if script else None,
                         "git_commit": e.get("git_commit"), "built_at": built, "code_changed_since": stale,
                         "params": e.get("params", {})})
    per_h = []
    for d in sorted(PROC.iterdir()):
        if d.is_dir() and d.name not in ("shared", "ai-village"):
            size, newest, n = dir_stats(d)
            per_h.append({"name": d.name, "bytes": size, "files": n, "mtime": iso(newest),
                          "provenance": (d / "_provenance.json").exists()})
    return {"tables": tables, "provenance": prov, "per_hypothesis": per_h}


# --------------------------------------------------------------------------------------------- holdout, overview

def calendar_meta() -> dict:
    def build():
        try:
            import polars as pl
            c = pl.read_parquet(PROC / "shared/calendar.parquet")
            g = (c.group_by("goal_no").agg(pl.col("pt_date").min().alias("start"), pl.col("pt_date").max().alias("end"),
                                           pl.col("regime").first().cast(pl.String), pl.col("holdout").any(), pl.len().alias("days")))
            meta = {int(r["goal_no"]): r for r in g.iter_rows(named=True)}
        except Exception:
            meta = {}
        try:
            sys.path.insert(0, str(ROOT / "infra/ai_village_overview"))
            src = (ROOT / "infra/ai_village_overview/figures.py").read_text()
            m = re.search(r"GOAL_SHORT\s*=\s*\{(.*?)\n\}", src, re.S)
            titles = dict((int(k), v) for k, v in re.findall(r"(\d+):\s*\"((?:[^\"\\]|\\.)*)\"", m.group(1))) if m else {}
        except Exception:
            titles = {}
        for g, t in titles.items():
            t = t.replace("\\\\#", "#").replace("\\#", "#").replace("~", " ").split("(Table")[0].strip()
            meta.setdefault(g, {})["title"] = t
        return meta
    return cached("calendar", 600, build)


def _held_refs(period: str, scope: str, held_goals: set[int], window_ids: list[str]) -> set[str]:
    """Held-out periods a confirmatory folder touched: its own G, plus #NN / #NN–#MM and NE ids named in its Role/Period lines."""
    refs = set()
    m = PERIOD_RE.match(period)
    goals = {int(m.group(2))} if m and m.group(2) else set()
    for a, b in re.findall(r"#(\d{1,2})\s*[–-]\s*#?(\d{1,2})", scope):
        goals |= set(range(int(a), int(b) + 1))
    goals |= {int(g) for g in re.findall(r"#(\d{1,2})\b", scope)}
    refs |= {f"G{g:02d}" for g in goals if g in held_goals}
    nes = set(re.findall(r"NE\d{2}", scope + " " + period))
    refs |= {w for w in window_ids if nes & set(re.findall(r"NE\d{2}", w))}
    return refs


def holdout(hs: list[dict]) -> dict:
    h = json.loads((HYP / "holdout.json").read_text())
    held = set(h["goal_periods_held_out"])
    wids = [w["id"] for w in h["ne_windows"]]
    used: dict[str, list] = {}
    for x in hs:
        for p in x["periods"]:
            if p["role"] != "confirmatory":
                continue
            planned = p["verdict"] in ("pending", "other")
            for ref in _held_refs(p["period"], p.get("scope", ""), held, wids):
                used.setdefault(ref, []).append({"h": x["id"], "verdict": p["verdict"], "path": p["path"], "planned": planned,
                                                 "via": p["period"]})
    cal = calendar_meta()
    goals = [{"period": f"G{g:02d}", "title": cal.get(g, {}).get("title", ""), "uses": used.get(f"G{g:02d}", [])}
             for g in h["goal_periods_held_out"]]
    windows = [{"id": w["id"], "start": w["start"], "end": w["end"], "why": w.get("why", ""), "uses": used.get(w["id"], [])}
               for w in h["ne_windows"]]
    pending = [{"h": x["id"], "scripts": x["confirm_scripts"]} for x in hs if x["confirm_scripts"] and not x["confirm_runs"]]
    return {"goals": goals, "windows": windows, "pending_confirm": pending}


def grid(hs: list[dict]) -> dict:
    cal = calendar_meta()
    periods = {}
    for x in hs:
        for p in x["periods"]:
            periods.setdefault(p["period"], {})[x["id"]] = {k: p[k] for k in ("verdict", "role", "path", "verdict_text")}

    def key(name):
        m = PERIOD_RE.match(name)
        return (0, int(m.group(2)), m.group(3) or "", name) if m.group(2) else (1, int(m.group(4)), "", name)
    rows = []
    for name in sorted(periods, key=key):
        m = PERIOD_RE.match(name)
        g = int(m.group(2)) if m.group(2) else None
        c = cal.get(g, {}) if g is not None else {}
        rows.append({"period": name, "goal": g, "title": c.get("title", "natural experiment" if g is None else ""),
                     "regime": c.get("regime"), "holdout": bool(c.get("holdout")), "start": c.get("start"),
                     "end": c.get("end"), "cells": periods[name]})
    return {"hypotheses": [x["id"] for x in hs], "rows": rows}


# --------------------------------------------------------------------------------------------- phase diagram

EST_PATH = PROC / "shared/per_period_estimates.parquet"
UNITS_PATH = PROC / "shared/period_units.parquet"


def estimates_mtime() -> float | None:
    try:
        return max(EST_PATH.stat().st_mtime, UNITS_PATH.stat().st_mtime)
    except OSError:
        return None


def _num(v):
    """JSON-safe float: NaN and inf become null (JSON.parse rejects NaN)."""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return float(f"{f:.6g}") if f == f and abs(f) != float("inf") else None


def unit_key(raw: str | None, goal) -> str | None:
    """Canonical unit key. 'G38' and bare '38' are the whole goal period -> 'G38'. A split unit keeps its id ('38a').
    Hypothesis-local windows keep the raw label ('local:...'). An empty label has no key (goal fallback only)."""
    if not raw:
        return None
    if raw.startswith("local:"):
        return raw
    m = re.fullmatch(r"G?(\d{1,2})", raw)
    if m:
        return f"G{int(m.group(1))}"
    return raw


def _build_estimates() -> dict:
    import polars as pl
    e = pl.read_parquet(EST_PATH)
    u = pl.read_parquet(UNITS_PATH)
    held_goals = set(json.loads((HYP / "holdout.json").read_text()).get("goal_periods_held_out", []))

    units = {}
    for r in u.iter_rows(named=True):
        units[r["unit_id"]] = {"key": r["unit_id"], "goal": r["goal_no"], "n_agents": r["n_agents"], "n_days": r["n_days"],
                               "n_rooms": len(r["rooms"] or []), "regime": r["regime"], "holdout": bool(r["holdout"]),
                               "first_day": r["first_day"], "last_day": r["last_day"], "reason": r["reason"], "split": True}
    by_goal: dict[int, list] = {}
    rooms_by_goal: dict[int, set] = {}
    for r in u.iter_rows(named=True):
        by_goal.setdefault(r["goal_no"], []).append(units[r["unit_id"]])
        rooms_by_goal.setdefault(r["goal_no"], set()).update(r["rooms"] or [])
    for g, us in by_goal.items():
        regs = sorted({x["regime"] for x in us if x["regime"]}, key=lambda s: ("I", "II", "III").index(s) if s in ("I", "II", "III") else 9)
        units[f"G{g}"] = {"key": f"G{g}", "goal": g, "n_agents": max(x["n_agents"] for x in us),
                          "n_days": sum(x["n_days"] for x in us), "n_rooms": len(rooms_by_goal[g]),
                          "regime": "/".join(regs) or None, "holdout": all(x["holdout"] for x in us) or g in held_goals,
                          "holdout_part": any(x["holdout"] for x in us) and not all(x["holdout"] for x in us),
                          "first_day": min(x["first_day"] for x in us), "last_day": max(x["last_day"] for x in us),
                          "n_split": len(us), "split": False}
        if len(us) == 1:  # a goal with one unit: the unit is the whole goal
            units.pop(us[0]["key"], None)

    slugs = {d.name.split("-")[0]: d.name for d in HYP.iterdir() if d.is_dir() and re.match(r"^H\d{2}-", d.name)}
    e = e.with_columns(pl.col("channel").fill_null(""), pl.col("method").fill_null(""))
    skeys = e.select("hypothesis", "statistic", "channel", "method").unique(maintain_order=True)
    sidx = {tuple(r): i for i, r in enumerate(skeys.iter_rows())}
    cols = {k: [] for k in ("s", "u", "k", "g", "est", "lo", "hi", "n", "role", "regime", "hold", "ci_kind", "ci_level",
                            "n_kind", "status", "post_hoc")}
    for r in e.iter_rows(named=True):
        cols["s"].append(sidx[(r["hypothesis"], r["statistic"], r["channel"], r["method"])])
        cols["u"].append(r["period_unit"] or "")
        cols["k"].append(unit_key(r["period_unit"], r["goal_no"]))
        cols["g"].append(r["goal_no"])
        cols["est"].append(_num(r["estimate"]))
        cols["lo"].append(_num(r["ci_lo"]))
        cols["hi"].append(_num(r["ci_hi"]))
        cols["n"].append(_num(r["n"]))
        cols["role"].append(r["role"])
        cols["regime"].append(r["regime"])
        cols["hold"].append(bool(r["holdout"]))
        cols["ci_kind"].append(r["ci_kind"])
        cols["ci_level"].append(_num(r["ci_level"]))
        cols["n_kind"].append(r["n_kind"])
        cols["status"].append(r["status"])
        cols["post_hoc"].append(r["post_hoc"])
    series = []
    for (h, st, ch, me), i in sidx.items():
        series.append({"i": i, "h": h, "slug": slugs.get(h), "stat": st, "channel": ch, "method": me})
    for i, s in enumerate(cols["s"]):  # per-series counts for the picker
        x = series[s]
        x.setdefault("_u", set()).add(cols["k"][i] or cols["u"][i])
        x["n_rows"] = x.get("n_rows", 0) + 1
        x["n_ci"] = x.get("n_ci", 0) + (cols["lo"][i] is not None and cols["hi"][i] is not None)
    for x in series:
        x["n_units"] = len(x.pop("_u"))
    titles = {g: m.get("title", "") for g, m in calendar_meta().items()}
    return {"mtime": iso(estimates_mtime()), "n_rows": e.height, "series": series, "rows": cols,
            "units": list(units.values()), "goal_titles": titles, "held_goals": sorted(held_goals)}


def estimates() -> dict:
    """Per-period estimates and unit covariates for the phase-diagram view. Rebuilt only when either parquet changes."""
    mt = estimates_mtime()
    if mt is None:
        return {"error": "per_period_estimates.parquet or period_units.parquet is missing"}
    hit = _cache.get("estimates")
    if hit and hit[0] == mt:
        return hit[1]
    val = _build_estimates()
    _cache["estimates"] = (mt, val)
    return val


# --------------------------------------------------------------------------------------------- log, git, ps, budget

def log_feed(n: int = 30) -> list[dict]:
    p = ROOT / "LOG.md"
    if not p.exists():
        return []
    lines = p.read_text(errors="replace").splitlines()
    out, date, cur = [], None, None
    for line in lines:
        if line.startswith("## "):
            if date is not None and len(out) >= n:
                break
            date = line[3:].strip()
            continue
        if date is None:
            continue
        if line.startswith("- "):
            cur = {"date": date, "md": line}
            out.append(cur)
        elif cur is not None and (line.startswith("  ") or not line.strip()):
            cur["md"] += "\n" + line
        elif line.startswith("---"):
            cur = None
    for e in out:
        e["md"] = e["md"].rstrip()
        line0 = e["md"].splitlines()[0][2:].strip()
        bold = re.match(r"\*\*(.+?)\*\*", line0)
        first = bold.group(1).rstrip(":. ") if bold else strip_md(line0)
        e["title"] = first if len(first) <= 140 else first[:137].rstrip() + "…"
    return out[:n]


def git_state() -> dict:
    def build():
        def run(*a):
            r = subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, timeout=10)
            return r.stdout.strip()
        commits = [dict(zip(("hash", "when", "subject"), l.split("\x1f"))) for l in run("log", "-8", "--format=%h\x1f%ar\x1f%s").splitlines() if l]
        dirty = [l for l in run("status", "--porcelain").splitlines() if l]
        return {"branch": run("rev-parse", "--abbrev-ref", "HEAD"), "commits": commits, "uncommitted": len(dirty)}
    return cached("git", 15, build)


def processes() -> list[dict]:
    def build():
        r = subprocess.run(["ps", "-axo", "pid=,pcpu=,pmem=,etime=,command="], capture_output=True, text=True)
        out = []
        for line in r.stdout.splitlines():
            parts = line.split(None, 4)
            if len(parts) < 5:
                continue
            cmd = parts[4]
            if "python" not in cmd or not re.search(r"hypotheses/|infra/|dashboard/|agenttesting", cmd):
                continue
            m = re.search(r"((?:hypotheses|infra|dashboard)/[^\s]+\.py)(.*)", cmd)
            out.append({"pid": int(parts[0]), "cpu": float(parts[1]), "mem": float(parts[2]), "elapsed": parts[3],
                        "script": m.group(1) if m else cmd[-90:], "args": (m.group(2).strip()[:60] if m else "")})
        return sorted(out, key=lambda p: -p["cpu"])
    return cached("ps", 4, build)


def budget() -> dict:
    def du(path: Path):
        if not path.exists():
            return None
        r = subprocess.run(["du", "-sk", str(path)], capture_output=True, text=True, timeout=120)
        try:
            return int(r.stdout.split()[0]) * 1024
        except (IndexError, ValueError):
            return None

    def build():
        limit = 20
        m = re.search(r"Storage budget:\s*(\d+)\s*GB", (ROOT / "CLAUDE.md").read_text())
        if m:
            limit = int(m.group(1))
        parts = {"data/raw": du(ROOT / "data/raw"), "data/processed": du(ROOT / "data/processed"), ".venv": du(ROOT / ".venv"),
                 ".git": du(ROOT / ".git"), "uv cache (shared)": du(Path.home() / ".cache/uv"),
                 "HF cache": du(Path.home() / ".cache/huggingface")}
        repo_total = du(ROOT)
        return {"limit_gb": limit, "parts": parts, "repo_total": repo_total}
    b = cached("budget", 300, build)
    spend = cached("jev", 60, lambda: round(sum(json.loads(l).get("cost", 0) or 0
                                                 for f in (PROC / "behavior_states").glob("jev_*.jsonl")
                                                 for l in f.open()), 4) if (PROC / "behavior_states").exists() else 0)
    return {**b, "jev_usd": spend}


def state() -> dict:
    t0 = time.time()
    hs = cached("hyp", 8, hypotheses)
    out = {
        "generated_at": iso(time.time()), "root": str(ROOT),
        "hypotheses": hs, "grid": grid(hs), "holdout": holdout(hs), "models": cached("models", 60, physics_models), "constants": cached("constants", 30, constants), "vetting": vetting(),
        "agents": cached("agents", 5, agents), "pipelines": cached("pipelines", 30, pipelines),
        "log": cached("log", 10, log_feed), "git": git_state(), "processes": processes(), "budget": budget(),
        "estimates_mtime": iso(estimates_mtime()),
    }
    out["collect_ms"] = round(1000 * (time.time() - t0))
    return out


if __name__ == "__main__":
    s = state()
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in s.items()
                      if k in ("hypotheses", "agents", "log", "processes", "collect_ms")}, indent=1))
