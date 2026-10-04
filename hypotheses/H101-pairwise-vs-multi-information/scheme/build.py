"""H101 scheme: item x agent co-usage matrices per non-holdout unit-day (codes only, no text).

Item = an H34 marker (hash) used in agent chat that day; family 'conv' (classes N, W, D) or 'proj' (class U).
Agent i's spin for item m on day d: 1 if i used m in a chat message that day. Active agents: >= 10 convention uses
that day (the same population for both families). Claude Code agent excluded. Held-out days are removed with
common.holdout_mask and calendar.holdout and asserted twice.

Output: data/processed/H101-pairwise-vs-multi-information/days/<unit>.npz with, per day k:
  conv_<k>, proj_<k>    uint8 T x N_d matrices (rows: items used by >= 1 active agent that day)
  convW_<k>             bool per conv item: class W (rare word)   (variant: drop W)
  convH_<k>, projH_<k>  bool per item: a human used it that day   (variant: drop exogenous items)
  agents_<k>, rooms_<k> agent codes and each agent's modal room that day
  days                  pt_dates
Usage: uv run python hypotheses/H101-pairwise-vs-multi-information/scheme/build.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H101-pairwise-vs-multi-information"
USES = ROOT / "data/processed/H34-idea-cascades/markers/uses.parquet"
MIN_USES = 10


def load(allow_holdout: bool = False, uses_path: Path = USES):
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "holdout"])
    ch = (pl.read_parquet(SH / "chat_core.parquet", columns=["pt_date", "goal_no", "speaker_kind", "agent", "room"])
          .with_row_index("msg").join(cal, on="pt_date", how="left"))
    if not allow_holdout:
        hm = np.array(holdout_mask(ch["pt_date"].to_list(), ch["goal_no"].to_list())) | ch["holdout"].fill_null(False).to_numpy()
        ch = ch.filter(~pl.Series(hm))
    ro = pl.read_parquet(SH / "roster.parquet")
    cc = ro.filter(pl.col("claude_code"))["agent"].to_list()
    u = pl.read_parquet(uses_path).join(ch, on="msg", how="inner")
    if not allow_holdout:
        assert not u["holdout"].fill_null(False).any()
    return ch, u, cc


def main():
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout"))
    build(pu)


def build(pu, allow_holdout: bool = False, uses_path: Path = USES):
    """allow_holdout=True only from analysis/confirm.py (Vivian's sign-off); uses_path then points at marker uses
    extracted for the held-out rows with idea_markers.uses_for_rows(..., allow_holdout=True)."""
    ch, u, cc = load(allow_holdout, uses_path)
    (OUT / "days").mkdir(parents=True, exist_ok=True)
    meta = []
    ag = u.filter((pl.col("speaker_kind") == "agent") & ~pl.col("agent").is_in(cc))
    hu = u.filter(pl.col("speaker_kind") == "human").select("pt_date", "marker").unique()
    # modal room per agent-day from agent chat
    room = (ch.filter(pl.col("speaker_kind") == "agent").group_by("pt_date", "agent", "room").agg(pl.len().alias("k"))
            .sort("k", descending=True).group_by("pt_date", "agent").agg(pl.col("room").first()))
    for r in pu.iter_rows(named=True):
        days = [d for d in r["days"]]
        if not allow_holdout:
            hmk = holdout_mask(days, [r["goal_no"]] * len(days))
            days = [d for d, h in zip(days, hmk) if not h]
        arrs = {}
        kept = []
        for d in days:
            x = ag.filter((pl.col("pt_date") == d) & (pl.col("goal_no") == r["goal_no"]))
            if x.height == 0:
                continue
            conv = x.filter(pl.col("cls") != 0)
            act = (conv.group_by("agent").agg(pl.len().alias("k")).filter(pl.col("k") >= MIN_USES)["agent"].sort().to_list())
            if len(act) < 3:
                continue
            k = len(kept)
            kept.append(d)
            hset = set(hu.filter(pl.col("pt_date") == d)["marker"].to_list())
            for fam, sub in (("conv", conv), ("proj", x.filter(pl.col("cls") == 0))):
                s = sub.filter(pl.col("agent").is_in(act)).select("marker", "agent", "cls").unique(["marker", "agent"])
                items = s["marker"].unique().sort().to_list()
                pos = {m: i for i, m in enumerate(items)}
                apos = {a: j for j, a in enumerate(act)}
                M = np.zeros((len(items), len(act)), np.uint8)
                if s.height:
                    M[[pos[m] for m in s["marker"].to_list()], [apos[a] for a in s["agent"].to_list()]] = 1
                arrs[f"{fam}_{k}"] = M
                arrs[f"{fam}H_{k}"] = np.array([m in hset for m in items], bool)
                if fam == "conv":
                    clsm = s.group_by("marker").agg(pl.col("cls").first()).sort("marker")
                    arrs[f"convW_{k}"] = (clsm["cls"].to_numpy() == 3)
            arrs[f"agents_{k}"] = np.array(act, np.int16)
            rr = room.filter(pl.col("pt_date") == d)
            rmap = dict(zip(rr["agent"].to_list(), rr["room"].to_list()))
            arrs[f"rooms_{k}"] = np.array([rmap.get(a, -1) if rmap.get(a) is not None else -1 for a in act], np.int16)
        if not kept:
            continue
        arrs["days"] = np.array(kept)
        np.savez_compressed(OUT / "days" / f"{r['unit_id']}.npz", **arrs)
        meta.append({"unit_id": r["unit_id"], "goal_no": r["goal_no"], "regime": r["regime"], "n_days": len(kept),
                     "N_med": float(np.median([len(arrs[f'agents_{k}']) for k in range(len(kept))])),
                     "T_conv": int(sum(arrs[f"conv_{k}"].shape[0] for k in range(len(kept)))),
                     "T_proj": int(sum(arrs[f"proj_{k}"].shape[0] for k in range(len(kept))))})
    pl.DataFrame(meta).write_parquet(OUT / "unit_meta.parquet")
    prov = {"built_by": "hypotheses/H101-pairwise-vs-multi-information/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "tables": ["chat_core", "calendar", "period_units", "roster"]},
                       {"source": "H34 marker uses (hashes)", "path": str(USES.relative_to(ROOT))}],
            "params": {"min_uses_active": MIN_USES, "families": {"conv": "N,W,D", "proj": "U"}},
            "built_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(pl.DataFrame(meta))


if __name__ == "__main__":
    main()
