"""Compare Jev label runs on the 200-window draft sample with the blind Claude labels (v1 definitions).

  uv run python infra/behavior_states/compare_labels.py                      # v2 and v3 (if present)
  uv run python infra/behavior_states/compare_labels.py --runs v2 v3 --json out.json

Inputs (data/processed/behavior_states/, gitignored): blind_draft.jsonl (id -> pt_date/agent/w), claude_labels_draft.jsonl
(blind Claude labels, v1 taxonomy), jev_draft_<run>.jsonl (Jev answers). Prints agreement and Cohen's kappa overall and by Jev
confidence band, the confusion pairs, and the flag/score agreements. No window text is printed.

Category maps (Jev -> Claude's v1 space): execute_task -> build_execute; idle_monitor (v2), idle and monitor_wait (v3) ->
idle_wait. A second, "monitor-aware" reference re-labels Claude's research_browse / idle_wait / verify_report windows whose
blind note describes monitoring or waiting for something as monitor_wait (rule fixed before looking at v3 answers); it is
only meaningful for v3, which has that class.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parents[2] / "data/processed/behavior_states"
TO_V1 = {"execute_task": "build_execute", "idle_monitor": "idle_wait", "idle": "idle_wait", "monitor_wait": "idle_wait"}
MONITOR_NOTE = re.compile(r"monitor|watch(ing|er)|poll|await|waiting (for|on)|standing by|stand by|checking .* for", re.I)
BANDS = [("conf>=0.8", 0.8, 1.01), ("0.5-0.8", 0.5, 0.8), ("conf<0.5", 0.0, 0.5)]


def kappa(a: list, b: list) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / n ** 2
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def spearman(x: list, y: list) -> float:
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def load(run: str):
    blind = {j["id"]: (j["pt_date"], j["agent"], j["w"]) for j in map(json.loads, open(D / "blind_draft.jsonl"))}
    claude = {blind[j["id"]]: j for j in map(json.loads, open(D / "claude_labels_draft.jsonl"))}
    jev = {}
    for j in map(json.loads, open(D / f"jev_draft_{run}.jsonl")):
        if j.get("answers"):
            jev[(j["pt_date"], j["agent"], j["w"])] = j["answers"]
    return claude, jev


def regimes() -> dict:
    import polars as pl
    cal = pl.read_parquet(D.parent / "shared/calendar.parquet", columns=["pt_date", "regime"])
    return dict(zip(cal["pt_date"], cal["regime"].cast(pl.Utf8)))


def monitor_ref(c: dict) -> str:
    lab = c["behavior"]
    if lab in ("research_browse", "idle_wait", "verify_report") and MONITOR_NOTE.search(c.get("note") or ""):
        return "monitor_wait"
    return lab


def evaluate(run: str) -> dict:
    claude, jev = load(run)
    keys = [k for k in claude if k in jev]
    jb = [jev[k]["behavior"]["choice"] for k in keys]
    jc = [jev[k]["behavior"].get("confidence") or 0.0 for k in keys]
    j1 = [TO_V1.get(x, x) for x in jb]
    cb = [claude[k]["behavior"] for k in keys]
    out = {"run": run, "n": len(keys), "jev_counts": dict(Counter(jb).most_common()),
           "behavior_v1": {"agree": sum(a == b for a, b in zip(j1, cb)) / len(keys), "kappa": kappa(j1, cb)}}
    for name, lo, hi in BANDS:
        idx = [i for i, c in enumerate(jc) if lo <= c < hi]
        out["behavior_v1"][name] = {"n": len(idx), "agree": (sum(j1[i] == cb[i] for i in idx) / len(idx)) if idx else None,
                                    "kappa": kappa([j1[i] for i in idx], [cb[i] for i in idx]) if idx else None}
    if any(x in ("monitor_wait", "idle") for x in jb):  # v3: monitor-aware 11-class reference
        jm = [{"execute_task": "build_execute", "idle": "idle_wait"}.get(x, x) for x in jb]
        cm = [monitor_ref(claude[k]) for k in keys]
        out["behavior_monitor_aware"] = {"agree": sum(a == b for a, b in zip(jm, cm)) / len(keys), "kappa": kappa(jm, cm),
                                         "n_ref_monitor": cm.count("monitor_wait"), "n_jev_monitor": jm.count("monitor_wait"),
                                         "both_monitor": sum(a == b == "monitor_wait" for a, b in zip(jm, cm))}
        for name, lo, hi in BANDS:
            idx = [i for i, c in enumerate(jc) if lo <= c < hi]
            out["behavior_monitor_aware"][name] = {"n": len(idx), "kappa": kappa([jm[i] for i in idx], [cm[i] for i in idx]) if idx else None,
                                                   "agree": (sum(jm[i] == cm[i] for i in idx) / len(idx)) if idx else None}
    reg = regimes()
    for rg in ("I", "II", "III"):
        idx = [i for i, k in enumerate(keys) if reg.get(k[0]) == rg]
        if idx:
            out["behavior_v1"][f"regime_{rg}"] = {"n": len(idx), "agree": sum(j1[i] == cb[i] for i in idx) / len(idx),
                                                 "kappa": kappa([j1[i] for i in idx], [cb[i] for i in idx])}
    out["confusions_v1"] = Counter(f"jev:{a} / claude:{b}" for a, b in zip(j1, cb) if a != b).most_common(12)
    for flag, ckey in (("blocked", "blocked"), ("others_work", "others_work"), ("addresses_participant", "responds_to_agent")):
        pairs = [((jev[k].get(flag) or {}).get("noul"), claude[k].get(ckey)) for k in keys]
        pairs = [(p >= 0.5, bool(c)) for p, c in pairs if p is not None and c is not None]
        if pairs:
            a, b = zip(*pairs)
            out[flag] = {"n": len(pairs), "agree": sum(x == y for x, y in pairs) / len(pairs), "kappa": kappa(list(a), list(b)),
                         "jev_pos": sum(a), "claude_pos": sum(b)}
    pr = [((jev[k].get("progress") or {}).get("score"), claude[k].get("progress")) for k in keys]
    pr = [(p, c) for p, c in pr if p is not None and c is not None]
    out["progress_spearman"] = spearman([p for p, _ in pr], [c for _, c in pr]) if pr else None
    ma = [((jev[k].get("message_act") or {}).get("choice"), claude[k].get("message_act")) for k in keys]
    ma = [(p, c) for p, c in ma if p and c]
    if ma:
        out["message_act"] = {"n": len(ma), "agree": sum(p == c for p, c in ma) / len(ma), "kappa": kappa([p for p, _ in ma], [c for _, c in ma])}
    out["mean_conf"] = sum(jc) / len(jc)
    return out


def pairwise(r1: str, r2: str) -> dict:
    _, a = load(r1)
    _, b = load(r2)
    keys = [k for k in a if k in b]
    x = [TO_V1.get(a[k]["behavior"]["choice"], a[k]["behavior"]["choice"]) for k in keys]
    y = [TO_V1.get(b[k]["behavior"]["choice"], b[k]["behavior"]["choice"]) for k in keys]
    return {"n": len(keys), "agree_v1": sum(p == q for p, q in zip(x, y)) / len(keys), "kappa_v1": kappa(x, y)}


def evidence(runs: list[str]) -> dict:
    """Label-free check on windows where the data settles the label (independent of what the Claude labeler could see):
    git printed a commit or push, or a deploy ran -> execute_task by the tie-breaker (communicate_external also accepted);
    no actions, chat or commands beyond pause/wait/scaffold -> idle (v1: idle_wait; v2: idle_monitor; v3: idle/monitor_wait)."""
    import polars as pl
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import assemble_v3 as A
    blind = [json.loads(l) for l in open(D / "blind_draft.jsonl")]
    keys = pl.DataFrame([{k: j[k] for k in ("pt_date", "agent", "w")} for j in blind])
    f = A.features(keys)
    chg = f.filter((pl.col("n_commit_ok") + pl.col("n_push_ok") + pl.col("n_deploy")) > 0)
    ch_keys = set(zip(chg["pt_date"], chg["agent"], chg["w"]))
    claude, _ = load(runs[0])
    res = {"n_change_windows": len(ch_keys)}
    ok = ("build_execute", "execute_task", "communicate_external")
    res["claude_execute_share"] = sum(claude[k]["behavior"] in ok for k in ch_keys if k in claude) / max(len(ch_keys), 1)
    for r in runs:
        _, jev = load(r)
        res[f"{r}_execute_share"] = sum(jev[k]["behavior"]["choice"] in ok for k in ch_keys if k in jev) / max(len(ch_keys), 1)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", default=[r for r in ("v1", "v2", "v3") if (D / f"jev_draft_{r}.jsonl").exists()])
    ap.add_argument("--json")
    ap.add_argument("--evidence", action="store_true", help="also run the label-free evidence check (needs turn_outcomes)")
    args = ap.parse_args()
    res = {r: evaluate(r) for r in args.runs}
    if len(args.runs) >= 2:
        res["pairwise"] = {f"{a}~{b}": pairwise(a, b) for i, a in enumerate(args.runs) for b in args.runs[i + 1:]}
    if args.evidence:
        res["evidence"] = evidence(args.runs)
    txt = json.dumps(res, indent=1, default=lambda v: None if isinstance(v, float) and math.isnan(v) else v)
    print(txt)
    if args.json:
        Path(args.json).write_text(txt)


if __name__ == "__main__":
    main()
