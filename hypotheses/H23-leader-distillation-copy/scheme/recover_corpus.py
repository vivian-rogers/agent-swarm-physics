"""H23 scheme step 2: recover the leader's training corpus from what the #best agents printed in #44.

The training files lived in the GitHub repo ai-village-agents/kimi-leader-finetune, which we do not fetch. Their rows
appear verbatim in the agents' bash turns (grep -n / cat / head / json.dumps(indent=2) outputs and heredocs).
This step parses every JSON object with a `chat_snippet` key out of turns_text.parquet, attributes it to a file and,
where the view shows it, a line number, and assembles:

    v7-aug-64 training set (kimi-leader-v7-aug-64 = roster agents 28 and 30):
        lines 1-56  = data/scenarios_v0_curated_v1.jsonl (51 base-Kimi self-distilled samples + 5 handcrafted drift rows)
        lines 57-61 = 5 validation_before_handoff rows of data/scenarios_v0_curated_v3_candidate.jsonl not in curated_v1
        lines 62-64 = 3 handcrafted validation rows (/tmp/handcrafted_validation_patches.jsonl, Opus 4.7)
    (composition from the build command at 2026-05-29 17:38:36 UTC; see the card's pipeline reconstruction).

Outputs (gitignored):
    data/processed/H23-leader-distillation-copy/G44/corpus_rows_text.parquet   every recovered row view (text sidecar)
    data/processed/H23-leader-distillation-copy/G44/corpus_text.parquet        one row per training-set row recovered
    data/processed/H23-leader-distillation-copy/G44/offline_text.parquet       v7-aug-64 offline eval outputs, if shown
    data/processed/H23-leader-distillation-copy/G44/corpus_summary.json        derived counts only (safe to quote)
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
G44 = ROOT / "data/processed/H23-leader-distillation-copy/G44"

LINEAGE_FILES = {
    "scenarios_v0_curated_v1.jsonl", "scenarios_v7_aug_v1.jsonl", "scenarios_v0_curated_v3_candidate.jsonl",
    "scenarios_v0_3samples_v2.jsonl", "scenarios_v0_02_3samples.jsonl", "handcrafted_drift_v1.jsonl",
    "handcrafted_validation_patches.jsonl", "v3_patch_scenarios.jsonl", "goal_validation_patch_candidates_v1.jsonl",
}
DEC = json.JSONDecoder()
JSONL_RE = re.compile(r"([\w.~/-]*?)([\w-]+\.jsonl)")
GREP_PREFIX = re.compile(r"(?:^|\n)(?:([^\s:]*?([\w-]+\.jsonl)):)?(\d+):\s*$")
ROW_HDR = re.compile(r"--- row (\d+) \(([^)]*)\) ---\s*$")


def objects_in(text: str):
    """Yield (start, obj, prefix_line) for each JSON object containing chat_snippet."""
    for m in re.finditer(r"\{\s*\"", text):
        try:
            o, end = DEC.raw_decode(text, m.start())
        except Exception:
            continue
        if isinstance(o, dict) and "chat_snippet" in o and "id" in o:
            ls = text.rfind("\n", 0, m.start()) + 1
            prev = text.rfind("\n", 0, max(ls - 1, 0)) + 1
            yield m.start(), end, o, text[ls:m.start()], text[prev:ls]


def attribute(cmd: str, field: str, prefix: str, prevline: str):
    """Return (file, line, how)."""
    files = [f for _, f in JSONL_RE.findall(cmd or "")]
    uniq = sorted(set(files))
    # grep -n with several files: "path/file.jsonl:12:"
    m = re.match(r"^\s*(?:\S*?([\w-]+\.jsonl)):(\d+):\s*$", prefix)
    if m:
        return m.group(1), int(m.group(2)), "grep_file_line"
    m = re.match(r"^\s*(\d+):\s*$", prefix)
    if m and len(uniq) == 1:
        return uniq[0], int(m.group(1)), "grep_line"
    m = re.match(r"^\s*(?:\S*?([\w-]+\.jsonl)):\s*$", prefix)
    if m:
        return m.group(1), None, "grep_file"
    m = ROW_HDR.search(prevline)
    if m and len(uniq) == 1:
        return uniq[0], int(m.group(1)), "row_header"
    if field == "command":
        # heredoc writing a file: cat > path.jsonl << EOF
        w = re.findall(r"cat\s*>+\s*(\S*?([\w-]+\.jsonl))", cmd or "")
        if w:
            return w[0][1], None, "heredoc"
        return (uniq[0] if len(uniq) == 1 else None), None, "command"
    return (uniq[0] if len(uniq) == 1 else None), None, "view"


def main():
    d = pl.read_parquet(G44 / "turns_text.parquet")
    views = []
    for r in d.iter_rows(named=True):
        for field in ("command", "output"):
            s = r[field]
            if not s or "chat_snippet" not in s:
                continue
            k = 0
            for start, end, o, prefix, prevline in objects_in(s):
                f, line, how = attribute(r["command"] or "", field, prefix, prevline)
                resp = o.get("ideal_leader_response", o.get("leader_response"))
                views.append({"turn_id": r["turn_id"], "agent": r["agent"], "t": r["t"], "field": field, "k": k,
                              "file": f, "line": line, "how": how, "id": str(o.get("id")),
                              "bucket": o.get("bucket"), "sample_index": o.get("sample_index"),
                              "source": o.get("source") if isinstance(o.get("source"), str) else None,
                              "chat_snippet": o.get("chat_snippet"),
                              "response": resp if isinstance(resp, str) else None,
                              "resp_key": "leader_response" if "leader_response" in o else "ideal_leader_response"})
                k += 1
    V = pl.DataFrame(views, infer_schema_length=None).sort("t", "turn_id", "field", "k")
    V.write_parquet(G44 / "corpus_rows_text.parquet", compression="zstd")

    # ---- assemble the 64-row v7-aug training set
    have: dict[int, dict] = {}          # v7-aug line -> row
    def put(line, row, how):
        if line in have:
            if have[line]["response"] != row["response"]:
                have[line].setdefault("conflict", 0)
                have[line]["conflict"] = have[line].get("conflict", 0) + 1
            return
        have[line] = {**row, "v7_line": line, "recovered_how": how}

    # pass 1: exact line views. curated_v1 line L == v7-aug line L for L <= 56 (v7-aug = curated_v1 + extras + hc).
    # The latest view of a line wins (closest to the 2026-05-29 training run); differing earlier views are counted.
    lined = (V.filter(pl.col("line").is_not_null() & pl.col("response").is_not_null()
                      & (pl.col("file").is_in(["scenarios_v7_aug_v1.jsonl", "scenarios_v0_curated_v1.jsonl"])))
             .filter((pl.col("file") == "scenarios_v7_aug_v1.jsonl") | (pl.col("line") <= 56))
             .sort("t", descending=True))
    for row in lined.iter_rows(named=True):
        put(row["line"], row, "v7_aug_line" if row["file"] == "scenarios_v7_aug_v1.jsonl" else "curated_line")
    # pass 2: rows 57-64 by id (v3 validation extras and handcrafted validation rows) from any lineage view
    hc_ids = ["validation_handcrafted_01", "validation_handcrafted_02", "validation_handcrafted_03"]
    for i, hid in enumerate(hc_ids):
        sub = V.filter((pl.col("id") == hid) & pl.col("response").is_not_null())
        if sub.height:
            put(62 + i, sub.row(0, named=True), "id_handcrafted")
    # the 5 v3 validation extras: validation_before_handoff rows of v3_candidate absent from curated_v1, in file order
    v3 = (V.filter((pl.col("file") == "scenarios_v0_curated_v3_candidate.jsonl")
                   & (pl.col("bucket") == "validation_before_handoff") & pl.col("response").is_not_null()))
    cur_ids = {(r["id"], r["sample_index"]) for r in have.values() if r["v7_line"] <= 56}
    extras = []
    for row in v3.sort("line", nulls_last=True).iter_rows(named=True):
        key = (row["id"], row["sample_index"])
        if key not in cur_ids and row["id"] not in [e["id"] for e in extras]:
            extras.append(row)
    # fall back to the patch source files for ids we know were validation patches
    if len(extras) < 5:
        for pid in ["validation_patch_01", "validation_patch_02", "goal_validation_patch_validation_01",
                    "goal_validation_patch_validation_02", "goal_validation_patch_deploy_01"]:
            if pid in [e["id"] for e in extras]:
                continue
            sub = V.filter((pl.col("id") == pid) & pl.col("response").is_not_null())
            if sub.height:
                extras.append(sub.row(0, named=True))
    for i, row in enumerate(extras[:5]):
        if 57 + i not in have:
            have[57 + i] = {**row, "v7_line": 57 + i, "recovered_how": "v3_validation_extra"}
    # pass 3: key-based membership. curated_v1 kept all 3 samples of both scenarios (_01, _02) in 7 buckets
    # (6 rows each in the v7-aug bucket counts), so every (id, sample_index) sample of those buckets is a member
    # whatever view shows it; drift edits do not touch these buckets. Latest view wins.
    FULL = {"admin_pivot", "disagreement_vote", "duplicate_loop", "memory_contamination", "peer_stuck",
            "infra_ambiguity", "validation_before_handoff"}
    placed_keys = {(r["id"], r["sample_index"]) for r in have.values()}
    samp = (V.filter(pl.col("response").is_not_null() & pl.col("sample_index").is_not_null()
                     & (pl.col("resp_key") == "ideal_leader_response")
                     & pl.col("id").str.contains(r"_0[12]$"))
            .sort("t", descending=True))
    keyed: dict = {}
    for row in samp.iter_rows(named=True):
        key = (row["id"], row["sample_index"])
        if key in placed_keys or key in keyed:
            continue
        keyed[key] = row
    extra_rows, unplaced = [], []
    for key, row in sorted(keyed.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        if row["bucket"] in FULL and row["sample_index"] in (0, 1, 2):
            extra_rows.append({**row, "v7_line": None, "recovered_how": "member_by_key"})
        else:
            unplaced.append(row)
    # handcrafted drift rows (all 5 are in curated_v1)
    for row in (V.filter((pl.col("file") == "handcrafted_drift_v1.jsonl") & pl.col("response").is_not_null())
                .unique(["id", "response"], keep="last").iter_rows(named=True)):
        if row["response"] not in {r["response"] for r in have.values()}:
            extra_rows.append({**row, "v7_line": None, "recovered_how": "handcrafted_drift_file",
                               "source": row.get("source") or "handcrafted"})
    rows = sorted(have.values(), key=lambda r: r["v7_line"]) + extra_rows

    def author(r):
        i, s = r["id"], (r.get("source") or "")
        if r.get("recovered_how") == "handcrafted_drift_file":
            return "handcrafted_drift"
        if r["v7_line"] and r["v7_line"] >= 62:
            return "handcrafted_opus47"
        if r["v7_line"] and 57 <= r["v7_line"] <= 61:
            return "patch_gpt55" if i.startswith("goal_validation") else "patch_kimi"
        if "handcrafted" in s or i.startswith("drift_patch") or (r.get("sample_index") is None and i.startswith("drift")):
            return "handcrafted_drift"
        return "base_kimi_distilled"

    out = []
    for r in rows:
        out.append({"v7_line": r["v7_line"], "member": True, "id": r["id"], "bucket": r["bucket"],
                    "sample_index": r["sample_index"],
                    "source": r.get("source"), "author": author(r), "recovered_how": r["recovered_how"],
                    "conflicts": r.get("conflict", 0), "chat_snippet": r["chat_snippet"], "response": r["response"]})
    for r in unplaced:
        out.append({"v7_line": None, "member": False, "id": r["id"], "bucket": r["bucket"],
                    "sample_index": r["sample_index"],
                    "source": r.get("source"), "author": "base_kimi_unplaced", "recovered_how": "unplaced_sample",
                    "conflicts": 0, "chat_snippet": r["chat_snippet"], "response": r["response"]})
    C = pl.DataFrame(out, infer_schema_length=None)
    C.write_parquet(G44 / "corpus_text.parquet", compression="zstd")

    # offline outputs of the deployed weights (eval files named *v7*aug* with leader_response)
    off = V.filter((pl.col("resp_key") == "leader_response") & pl.col("file").str.contains("v7").fill_null(False)
                   & pl.col("file").str.contains("aug").fill_null(False))
    off.unique(["id", "response"]).write_parquet(G44 / "offline_text.parquet", compression="zstd")

    placed_lines = sorted(r["v7_line"] for r in out if r["v7_line"])
    summ = {
        "views_parsed": V.height,
        "views_by_file": dict(Counter(V["file"].fill_null("?").to_list()).most_common()),
        "views_by_how": dict(Counter(V["how"].to_list()).most_common()),
        "v7aug_rows_total": 64,
        "v7aug_rows_recovered_with_line": len(placed_lines),
        "v7aug_rows_recovered_member": int(sum(1 for r in out if r["member"])),
        "v7aug_lines_missing": [i for i in range(1, 65) if i not in placed_lines],
        "recovered_by_author": dict(Counter(r["author"] for r in out if r["member"])),
        "recovered_by_bucket": dict(Counter(r["bucket"] for r in out if r["member"])),
        "expected_by_bucket": {"validation_before_handoff": 14, "drift_to_old_goal": 7, "admin_pivot": 6,
                               "disagreement_vote": 6, "duplicate_loop": 6, "memory_contamination": 6,
                               "peer_stuck": 6, "infra_ambiguity": 6, "goal_kickoff": 5, "deadline_pressure": 2},
        "unplaced_by_bucket": dict(Counter(r["bucket"] for r in out if not r["member"])),
        "line_conflicts": int(sum(r["conflicts"] for r in out)),
        "unplaced_distilled_samples": len(unplaced),
        "offline_v7aug_outputs": off.unique(["id", "response"]).height,
        "response_chars_member": {"median": float(pl.Series([len(r["response"]) for r in out if r["member"]]).median()),
                                  "total": int(sum(len(r["response"]) for r in out if r["member"]))},
    }
    (G44 / "corpus_summary.json").write_text(json.dumps(summ, indent=1, default=str))
    print(json.dumps(summ, indent=1, default=str))


if __name__ == "__main__":
    main()
