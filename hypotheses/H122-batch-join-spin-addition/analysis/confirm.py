"""H122 confirmatory run on the LOCKED HOLDOUT: NE33 (batch join of Muse Spark 1.3, Gemini 3.8 Flash on 2026-09-03 and
GPT-6 Astra on 09-04). Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: runs only with BOTH `--confirm` and H122_CONFIRM=1, and only if `holdout_ledger.check` allows '#51-tail'.
Otherwise it refuses. `--dry-run` runs the identical scoring on the exploratory NE32 files (non-holdout) and writes to
a scratch directory.

Design (identical to round 1; scheme/build.py + h122lib, B = 2000 for log-loss differences, B = 200 for parameters):
  PRE  = up to 5 non-holdout active days before 09-03 (08-27 ... 09-02; recent joiners GLM-5.3 Flash and Claude
         Fable 5.1 excluded from incumbents); P12 = 09-03, 09-04 (non-holdout; blind: no H122 statistic has touched
         incumbents' calls on these days); F37 = 09-07 ... 09-11 (held out).
Frozen predictions (round 1: 6/10 events had the constant shift beating couplings, NE32 among them; the HH is
predicted to FAIL again):
  C1  HH test (kill): MJ beats MC on P12 (Delta LL = LL(MC) - LL(MJ) CI > 0). Predicted: NOT met; MC >= MJ.
      Kill outcome (MC beats MJ, CI < 0) is the round-1 expectation.
  C2  Read vs in-flight: LL(MJ_pl) - LL(MJ) > 0 (point). Round 1: 4/10 events.
  C3  Fast step: J_N(P12) / J_N(F37) in [0.5, 2] when both are resolved (CI excluding 0). Round 1: 2/2 resolved events.
  C4  Address gating among newcomer reads: J_named > J_unnamed (F37). Round 1: 8/10 events.
Disclosure: H98 examined NE33 joiners' content on 09-03/04 (different statistic and modality). Planned users of the
#51 tail are many (see hypotheses/holdout.md); this is the first use of incumbent per-call talk around NE33.

Usage:
  uv run python hypotheses/H122-batch-join-spin-addition/analysis/confirm.py --dry-run
  H122_CONFIRM=1 uv run python hypotheses/H122-batch-join-spin-addition/analysis/confirm.py --confirm
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h122lib as L  # noqa: E402

ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))
EXPL = ROOT / "data/processed/H122-batch-join-spin-addition"
OUT = EXPL / "confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h122_confirm_dryrun"
FROZEN = dict(C3=(0.5, 2.0))


def _build():
    spec = importlib.util.spec_from_file_location("h122build", HERE.parent / "scheme" / "build.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def score(calls_path: Path, N: dict) -> dict:
    df = L.prep(pl.read_parquet(calls_path))
    fit = L.fit_models(df, N)
    sc = L.scores(fit, B=2000, seed=1)
    bp = L.boot_params(df, N, B=200, seed=2)
    par = fit["par"]
    out = {"scores": sc, "params": {k: v for k, v in par.items() if k != "pre"}, "boot": bp}
    out["C1"] = bool(sc["d_C_J_lo"] > 0)
    out["kill_MC_wins"] = bool(sc["d_C_J_hi"] < 0)
    out["C2"] = bool(sc["d_PL_J"] > 0)
    resolved = (bp["J_N_lo"] > 0 or bp["J_N_hi"] < 0) and (bp["J_N_p12_lo"] > 0 or bp["J_N_p12_hi"] < 0)
    ratio = par["J_N_p12"] / par["J_N"] if abs(par["J_N"]) > 1e-9 else np.nan
    out["C3"] = bool(resolved and FROZEN["C3"][0] <= ratio <= FROZEN["C3"][1]) if resolved else None
    out["C3_detail"] = {"ratio": ratio, "resolved": resolved}
    out["C4"] = bool(par["J_named"] > par["J_unnamed"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if a.dry_run:
        e = pl.read_parquet(EXPL / "events.parquet").filter(pl.col("event") == "NE32").to_dicts()[0]
        out = score(EXPL / "calls" / "NE32.parquet", {0: e["N_pre"], 1: e["N_p12"], 2: e["N_f37"]})
        SCRATCH.mkdir(parents=True, exist_ok=True)
        (SCRATCH / "dryrun.json").write_text(json.dumps({"sha256": sha, "standin": "NE32", **out}, indent=1, default=float))
        print(json.dumps({k: v for k, v in out.items() if k not in ("boot",)}, indent=1, default=float))
        return
    if not (a.confirm and os.environ.get("H122_CONFIRM") == "1"):
        sys.exit("refusing: confirmatory run needs --confirm and H122_CONFIRM=1 (Vivian's sign-off)")
    import holdout_ledger as HL
    chk = HL.check("H122", "#51-tail", "talk", ["other"])
    if not chk["allowed"]:
        sys.exit(f"refusing: holdout ledger blocks #51-tail: {chk['prior_runs_same_family']}")
    B = _build()
    cal = pl.read_parquet(SH / "calendar.parquet").sort("pt_date")
    ros = pl.read_parquet(SH / "roster.parquet")
    ev = B.events_table(cal, ros)
    e = ev.filter(pl.col("event") == "NE33").to_dicts()[0]
    days = cal["pt_date"].to_list()
    i1 = days.index(e["day1"])
    e["f37"] = [d for d in days[i1 + 2: i1 + 7]]           # 09-07 ... 09-11 (held out)
    assert e["f37"][0] == "2026-09-07", e["f37"]
    rj = [a2 for e2 in ev.to_dicts() if e["ix1"] - B.RECENT_JOIN <= e2["ix1"] < e["ix1"] for a2 in e2["newcomers"]]
    e["recent_joiners"] = rj
    cw, lt, cc, cca = B.load_shared(allow_holdout=True)
    meta = B.build_event(e, cw, lt, cc, cca, cal, out_dir=OUT, allow_holdout=True)
    out = score(OUT / "calls" / "NE33.parquet", {0: meta["N_pre"], 1: meta["N_p12"], 2: meta["N_f37"]})
    out["meta"] = meta
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "confirm_result.json").write_text(json.dumps({"sha256": sha, **out}, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "boot"}, indent=1, default=float))


if __name__ == "__main__":
    main()
