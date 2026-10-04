"""Post hoc (2026-10-04, after the replication runs): LOCO skill split into early rows (class read 0-2 calls ago) and
late rows (3-30 calls ago only), to locate where the one-lever model loses to the free fit.
Usage: uv run python analysis/loco_split.py --goal 51"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h59lib as L

ap = argparse.ArgumentParser(); ap.add_argument("--goal", type=int, required=True); a = ap.parse_args()
d = L.arrays(L.load(a.goal)); b = L.baseline(d); kd = L.KD(d, b["off"]); cls = L.powered(d)
lo = L.loco(d, kd, cls, nboot=50)
out = {c: {"split": x["split_early_late"], "T": x["T"]} for c, x in lo.items()}
od = L.OUT / f"G{a.goal:02d}"; od.mkdir(parents=True, exist_ok=True)
(od / "loco_split.json").write_text(json.dumps(out, indent=1))
for c, x in out.items():
    print(a.goal, c, {m: {k: round(v, 1) for k, v in s.items()} for m, s in x["split"].items()})
