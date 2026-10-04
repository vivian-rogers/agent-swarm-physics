"""H102 confirmatory script (LOCKED HOLDOUT). Written 2026-10-04 after exploratory round 1. NOT RUN.

Frozen predictions (thresholds fixed from round 1, before any holdout data is loaded):
  C1 domains: in each held-out two-room goal period among #45-#50 with >= 3 stayers per room (>= 2 days), the
     bimodality D exceeds its relabel 95th percentile (p < 0.05); where the room kickoffs differ (whitened
     cos < 0.95), D >= 2.                                                                                      [0.65]
  C2 sharp wall, no carry: in the #51 tail (2026-09-07 -> 09-21; needs #focus in use), every #general hopper with
     >= 3 hop-days has s(home) below the #general stayers' 95th percentile. No qualifying hopper -> void.      [0.6]
  C3 axis is not the instruction text: where room kickoffs differ, |cos(u, u_f)| has direction-null p > 0.05.  [0.6]
Primary instrument: bge_small style_resid statement vectors, day-centred.

Reuse disclosure (hypotheses/holdout.md): #45-#50 content and the #51 tail are planned by many content hypotheses
(H26, H47, H81-H83, H98 among them); H47's C1 (room contrast on #45-#47, #50) is the closest cousin. Disclose in the
card and LOG.md before running.

Safeguards: refuses without --confirm --i-understand-this-uses-the-locked-holdout; refuses unless this file, the card,
h102lib.py, run.py and scheme/build.py are tracked and unmodified; calls holdout_ledger.check() per target;
--dry-run uses non-holdout stand-ins (#41, #42, #44 for C1/C3; 51g for C2) and asserts no held-out row is loaded.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h102lib as L  # noqa: E402

ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

FILES = [f"hypotheses/H102-room-domain-walls/{f}" for f in
         ("analysis/confirm.py", "README.md", "analysis/h102lib.py", "analysis/run.py", "scheme/build.py")]


def git_clean() -> bool:
    for f in FILES:
        tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", f], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", f], capture_output=True, text=True).stdout.strip()
        if not tracked or dirty:
            print(f"refusing: {f} is untracked or modified", file=sys.stderr)
            return False
    return True


def load_build():
    spec = importlib.util.spec_from_file_location("h102build", ROOT / "hypotheses/H102-room-domain-walls/scheme/build.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def kickoff_dir(goal, model="bge_small"):
    """Whitened unit room-kickoff difference for a goal, or None if the room kickoffs do not differ."""
    import embed_models as EM
    g = pl.read_parquet(ROOT / "data/processed/shared/embeddings/goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    f = g.filter((pl.col("goal_no") == goal) & (pl.col("kind") == "kickoff_room"))
    rb, rr = f.filter(pl.col("room") == L.BEST), f.filter(pl.col("room") == L.REST)
    if not (rb.height and rr.height):
        return None
    gv = np.load(ROOT / "data/processed/shared/embeddings/goal_vectors.npy").astype(np.float32)
    W = EM.load_whitener("III", 32, model)
    vb, vr = W(gv[rb["gid"][0]][None])[0], W(gv[rr["gid"][0]][None])[0]
    vb, vr = vb / np.linalg.norm(vb), vr / np.linalg.norm(vr)
    if vb @ vr >= 0.95:
        return None
    d = vb - vr
    return d / np.linalg.norm(d)


def evaluate(st, X, dom, rd, units, tail_unit):
    st = st.with_columns(pl.int_range(pl.len()).alias("row"))
    Xc = L.day_center(st, X)
    out = {"units": {}}
    c1, c3 = [], []
    for u in units:
        fr = L.unit_frame(st, dom, u)
        A, B = L.rooms_of(dom, u)
        if A is None:
            continue
        ah = L.agent_halves(fr, Xc)
        nA = sum(1 for v in ah.values() if v[0] == A and v[1] == "stayer" and v[3] is not None and v[4] is not None)
        nB = sum(1 for v in ah.values() if v[0] == B and v[1] == "stayer" and v[3] is not None and v[4] is not None)
        if nA < 3 or nB < 3:
            continue
        bt = L.bimodality_test(ah, A, B, n_null=1000, seed=1)
        bt.pop("wc", None)
        uf = kickoff_dir(int(u[1:]))
        ok = bt["p"] < 0.05 and (uf is None or bt["D"] >= 2)
        c1.append(ok)
        r = {"bimodality": bt, "fielded": uf is not None}
        if uf is not None:
            fa = L.field_alignment(ah, A, B, uf)
            r["field_alignment"] = fa
            c3.append(fa["p"] > 0.05)
        out["units"][u] = r
    out["C1"] = all(c1) if c1 else None
    out["C3"] = all(c3) if c3 else None
    out["C2"] = None
    if tail_unit is not None:
        fr = L.unit_frame(st, dom, tail_unit)
        if fr.height and fr.filter(pl.col("role") == "hopper").height:
            ah = L.agent_halves(fr, Xc)
            hp = L.hopper_positions(fr, Xc, ah, L.GENERAL, L.FOCUS)
            q = {k: v for k, v in hp["hoppers"].items()
                 if sum(1 for d in v["days"].values() if d["n_all"] > d["n_home"]) >= 3}
            out["tail_hoppers"] = {k: {"s_home": v["s_home"], "n_other": v["n_other"]} for k, v in q.items()}
            out["tail_stayers_p95"] = hp["home_stayers_p95"]
            if q:
                out["C2"] = all(v["s_home"] is not None and v["s_home"] < hp["home_stayers_p95"] for v in q.values())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ok", action="store_true")
    a = ap.parse_args()
    B = load_build()
    if a.dry_run:
        st, Xs, dom, rd = B.main(write=False)
        assert not any(holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())), "held-out row in dry run"
        out = evaluate(st, Xs[("style_resid", "bge_small")].astype(np.float64), dom, rd, ["G41", "G42", "G44"], "51g")
        ref = json.loads((L.DATA / "results/raw_all.json").read_text())["bge_small_style_resid"]["units"]
        for u in out["units"]:
            assert abs(out["units"][u]["bimodality"]["D"] - ref[u]["bimodality"]["D"]) < 0.01, u
        dest = L.DATA / "confirm"; dest.mkdir(exist_ok=True)
        (dest / "confirm_dryrun.json").write_text(json.dumps(out, indent=1, default=float))
        print("dry run ok:", {k: out[k] for k in ("C1", "C2", "C3")})
        return
    if not (a.confirm and a.ok):
        sys.exit("refusing: pass --confirm --i-understand-this-uses-the-locked-holdout (needs Vivian's sign-off)")
    if not git_clean():
        sys.exit(1)
    import holdout_ledger as HL
    for t in ["G45", "G46", "G47", "G48", "G49", "G50", "#51-tail"]:
        c = HL.check("H102", t, "content", None)
        print(t, "allowed" if c["allowed"] else "BLOCKED", "disclosure needed" if c["needs_disclosure"] else "")
        if not c["allowed"]:
            sys.exit(f"refusing: {t} blocked by the holdout ledger")
    st, Xs, dom, rd = B.main(goals=[45, 46, 47, 48, 49, 50, 51], allow_holdout=True, write=False)
    out = evaluate(st, Xs[("style_resid", "bge_small")].astype(np.float64), dom, rd,
                   ["G45", "G46", "G47", "G48", "G49", "G50"], "51tail")
    dest = L.DATA / "confirm"; dest.mkdir(exist_ok=True)
    (dest / "confirm_result.json").write_text(json.dumps(out, indent=1, default=float))
    print({k: out[k] for k in ("C1", "C2", "C3")})


if __name__ == "__main__":
    main()
