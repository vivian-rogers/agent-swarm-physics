"""H41 confirmatory test on the LOCKED HOLDOUT. Written after round 1; NOT RUN.

  uv run python hypotheses/H41-readout-light-cone/analysis/confirm.py --dry-run           # stand-ins (non-holdout), safe
  uv run python hypotheses/H41-readout-light-cone/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout

Targets (see ../README.md, "Confirmatory predictions"):
  T1  #51 tail (2026-09-07 -> 09-21)             one big room + #focus; the largest replication target   (primary)
  T2  #47 (2026-06-15 -> 06-19)                  two rooms (#best/#rest): the cage test
  T3  #28 (regime I)                             one room, scheduled chat calls
  T4  #46-#50 onboarding / isolation rooms        (NE21+NE23 window): agents alone in a room
Stand-ins for --dry-run: T1 #51 08-24 -> 09-04, T2 #42, T3 #30, T4 #51 07-06 -> 07-23.

The frozen predictions are hashed (SHA-256) and written to confirm/sealed_<mode>.json before any held-out text is read.
Held-out chat text is read in memory only, hashed with H34's marker rule, and never written.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(HERE))
sys.path.append(str(ROOT / "hypotheses/H34-idea-cascades/scheme"))  # after ours: H34 also has a build.py
import h41core as C  # noqa: E402
import build as BLD  # noqa: E402
import h41stats as S  # noqa: E402
from explore import fix_cross, channel_label  # noqa: E402

OUTD = C.OUT / "confirm"

FROZEN = {
    "written": "2026-10-04 (after round 1, before any holdout use)",
    "C1_gating_matched": "delay-matched J_mh (in-flight vs first post-entry talk call, MH over delay-since-t0 bins) has "
                         "day-bootstrap lower CI > 1 in T1, and in at least 2 of {T1, T2, T3}",
    "C2_within_room_cone": "robust acausal share among within-room adoptions <= 0.03 in T1, T2 and T3",
    "C3_cage": "T2: >= 0.60 of cross-room adoptions outside the logged cone AND cross/within adoption hazard per "
               "talk call (2 h) <= 0.20",
    "C4_isolation": "T4: every adoption by an agent alone in a room of an item first used in another room is outside the "
                    "logged cone (definitional check of the pipeline) and there are >= 5 such adoptions OR none (reported)",
    "C5_unmatched_report": "pre-registered unmatched J_in is reported; no criterion (round 1 showed the recency confound)",
    "C6_velocity_talk": "median talk calls per hop <= 3 in T1 and T2 (regime III)",
    "supported_if": "C1 and C2 pass; the cage claim is confirmed if C3 passes",
}

TARGETS = {
    "confirm": {
        "T1": dict(goal=51, days=("2026-09-07", "2026-09-21")),
        "T2": dict(goal=47, days=None),
        "T3": dict(goal=28, days=None),
        "T4": dict(goals=[46, 47, 48, 49, 50], days=None),
    },
    "dry": {
        "T1": dict(goal=51, days=("2026-08-24", "2026-09-05")),
        "T2": dict(goal=42, days=None),
        "T3": dict(goal=30, days=None),
        "T4": dict(goals=[51], days=("2026-07-06", "2026-07-24")),
    },
}


def seal(mode: str) -> str:
    OUTD.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(FROZEN, sort_keys=True).encode()
    h = hashlib.sha256(blob).hexdigest()
    (OUTD / f"sealed_{mode}.json").write_text(json.dumps({"sha256": h, "frozen": FROZEN,
                                                          "sealed_at": dt.datetime.now(dt.timezone.utc).isoformat()}, indent=1))
    return h


def markers_for(sk: C.Skeleton, start_t: float):
    """Hash markers in the target's chat (text in memory only). Novel = not used in the non-holdout corpus before start."""
    import markers as M  # H34, read-only
    M.dictionary()
    ros = M.roster_full_names(pl.read_parquet(C.SH / "roster.parquet")["name"].to_list())
    ids = sk.msgs.select("message_id", "mrow")
    txt = (pl.scan_parquet(C.SH / "chat_text.parquet").select("message_id", "text")
           .join(ids.lazy(), on="message_id", how="inner").collect())
    rows = []
    for mid, t in zip(txt["message_id"].to_list(), txt["text"].to_list()):
        for c, x in M.extract(t, ros):
            rows.append((mid, M.marker_id(c, x), M.CLS[c]))
    del txt
    art = pl.read_parquet(C.SH / "artifacts.parquet", columns=["artifact", "kind"])
    am = (pl.read_parquet(C.SH / "artifact_mentions.parquet", columns=["artifact", "source", "how", "message_id"])
          .filter((pl.col("source") == "chat") & pl.col("how").cast(pl.Utf8).is_in(["url", "bare"]))
          .join(art, on="artifact").filter(pl.col("kind").cast(pl.Utf8).is_in(["repo", "site", "file"]))
          .join(ids, on="message_id", how="inner"))
    for mid, a in zip(am["message_id"].to_list(), am["artifact"].to_list()):
        rows.append((mid, M.marker_id("U", str(a)), 0))
    uses = pl.DataFrame({"message_id": [r[0] for r in rows], "marker": [r[1] for r in rows],
                         "cls": [r[2] for r in rows]}, schema={"message_id": pl.Utf8, "marker": pl.Int64, "cls": pl.UInt8}
                        ).unique(["message_id", "marker"])
    fs = pl.read_parquet(C.OUT / "markers/first_seen.parquet")
    old = fs.filter(pl.col("first_t").dt.epoch("us") / 1e6 < start_t).select("marker")
    nov = uses.join(old, on="marker", how="anti").select("marker", "cls").unique("marker")
    u = (uses.join(nov.select("marker"), on="marker", how="inner")
         .join(sk.msgs.select("message_id", "mrow", "t", "room", "kind", "agent", "node", "ci_talk", "pt_date"),
               on="message_id", how="inner").sort("marker", "t", "mrow"))
    return u, nov


def run_target(spec: dict, include_holdout: bool):
    cal = C.calendar()
    goals = spec.get("goals", [spec.get("goal")])
    out = []
    for g in goals:
        df = None
        if spec.get("days"):
            a, b = spec["days"]
            df = lambda d, a=a, b=b: a <= d < b
        sk = C.load_skeleton(g, cal, days_filter=df, include_holdout=include_holdout)
        if len(sk.c_t) == 0:
            continue
        u, nov = markers_for(sk, sk.t_min)
        ri = C.RoomIndex(sk)
        items, adf, hz, _ = BLD.analyze(sk, u, nov, cal, ri)
        out.append((g, sk, adf, hz, ri))
    return out


def stats_for(parts):
    adf = pl.concat([fix_cross(p[2]) for p in parts if p[2].height], how="vertical_relaxed") if parts else pl.DataFrame()
    hz = pl.concat([p[3] for p in parts if p[3].height], how="vertical_relaxed") if parts else pl.DataFrame()
    r = {}
    if adf.height:
        r["n_adopt"] = adf.height
        vs = S.violation_shares(adf, B=300)
        r.update({k: vs[k] for k in ["acaus", "acaus_rob", "acaus_rob_within", "acaus_rob_cross", "share_cross"]})
        r["velocity"] = S.velocity(adf)
    if hz.height:
        hm = S.hazard_jump_mh(hz, B=500)
        hj = S.hazard_jump(hz, B=500)
        r["J_mh"], r["J_mh_ci"] = hm.get("J_mh"), hm.get("J_mh_ci")
        r["J_in"], r["J_in_ci"] = hj.get("J_in"), hj.get("J_in_ci")
        inr = hz.group_by("in_room0").agg(pl.col("adopt").sum(), pl.col("at_risk").sum())
        d = {row["in_room0"]: row["adopt"] / row["at_risk"] for row in inr.iter_rows(named=True) if row["at_risk"]}
        r["cage_ratio"] = d.get(False, np.nan) / d.get(True, np.nan) if d.get(True) else np.nan
    return r, adf


def isolation(parts):
    n, acaus = 0, 0
    for g, sk, adf, hz, ri in parts:
        if adf.height == 0:
            continue
        agents = sorted(int(x) for x in sk.agents)  # every agent with receiving calls, not only adopters
        for a, t, t0, r0, ic in zip(adf["agent"].to_list(), adf["t_use"].to_list(), adf["t0"].to_list(),
                                    adf["room0"].to_list(), adf["in_cone"].to_list()):
            r = ri.at(a, t)
            if r in (r0, 0) or r < 0 or r0 in ri.rooms_in(a, t0, t):  # never in the source's room between t0 and use
                continue
            if all(ri.at(b, t) != r for b in agents if b != a):
                n += 1
                acaus += int(not ic)
    return dict(n_isolated=n, n_isolated_acausal=acaus)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.confirm and not a.ack:
        sys.exit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
    if not a.confirm and not a.dry_run:
        sys.exit("choose --dry-run (stand-ins) or --confirm --i-understand-this-uses-the-locked-holdout")
    mode = "confirm" if a.confirm else "dry"
    h = seal(mode)
    print("sealed predictions sha256", h)
    res = {"mode": mode, "sha256": h}
    for tname, spec in TARGETS[mode].items():
        parts = run_target(spec, include_holdout=(mode == "confirm"))
        r, adf = stats_for(parts)
        if tname == "T4":
            r.update(isolation(parts))
        res[tname] = r
        print(tname, json.dumps(r, default=str)[:600], flush=True)
    t1, t2, t3, t4 = (res.get(k, {}) for k in ("T1", "T2", "T3", "T4"))
    lo = lambda r: (r.get("J_mh_ci") or (np.nan, np.nan))[0]
    c1 = bool(lo(t1) > 1 and sum(lo(r) > 1 for r in (t1, t2, t3)) >= 2)
    c2 = all((r.get("acaus_rob_within") is not None and r["acaus_rob_within"] <= 0.03) for r in (t1, t2, t3))
    c3 = bool((t2.get("acaus_rob_cross") or 0) >= 0.60 and (t2.get("cage_ratio") or np.inf) <= 0.20)
    c4 = bool(t4.get("n_isolated", 0) == t4.get("n_isolated_acausal", -1))
    c6 = all((r.get("velocity", {}).get("talk_med") or 99) <= 3 for r in (t1, t2))
    res["checks"] = dict(C1=c1, C2=c2, C3=c3, C4=c4, C6=c6)
    res["supported"] = bool(c1 and c2)
    res["cage_confirmed"] = c3
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / f"result_{mode}.json").write_text(json.dumps(res, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o)))
    print(json.dumps(res["checks"]), "supported" if res["supported"] else "not supported")


if __name__ == "__main__":
    main()
