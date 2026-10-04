"""H13 confirmatory test on the LOCKED HOLDOUT (card: "Confirmatory predictions for the locked holdout (C1-C6)").

NOT RUN in round 1. It refuses to touch held-out data unless called with BOTH flags:
    uv run python hypotheses/H13-family-fields/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
Dry run (exercises every code path on NON-holdout stand-in units, writes to data/processed/H13-family-fields/confirm_dryrun/):
    uv run python hypotheses/H13-family-fields/analysis/confirm.py --dry-run

Pipeline: build the H13 scheme for the held-out units (scheme/build.py: build_units, allow_holdout=True) into
data/processed/H13-family-fields/confirm/; run explore.run_unit on each (same estimators, thresholds and nulls as
exploration); then the S-a room check, the style-feature-only family test, the exploration -> holdout family-field
transfer (fixed random-regrouping null), random-effects summaries, and the mechanical verdicts below.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h13lib as L  # noqa: E402
import explore as E  # noqa: E402
import build as B  # noqa: E402

DATA = E.DATA
CARD = HERE.parent / "README.md"

HOLDOUT_UNITS = {
    "45a": ("G45", 45, "III", "2026-06-01", "2026-06-02"),
    "45b": ("G45", 45, "III", "2026-06-03", "2026-06-05"),
    "46a": ("G46", 46, "III", "2026-06-08", "2026-06-10"),
    "46b": ("G46", 46, "III", "2026-06-11", "2026-06-13"),
    "47": ("G47", 47, "III", "2026-06-15", "2026-06-19"),
    "49": ("G49", 49, "III", "2026-06-23", "2026-06-26"),
    "50a": ("G50", 50, "III", "2026-06-29", "2026-06-30"),
    "50b": ("G50", 50, "III", "2026-07-01", "2026-07-03"),
    "51t": ("G51", 51, "III", "2026-09-07", "2026-09-18"),
}
# non-holdout stand-ins for --dry-run (code-path test only; C3 overlaps exploration there by construction)
DRYRUN_UNITS = {k: B.UNITS[k] for k in ("39", "41", "42", "38a", "40", "44", "51c", "51e")}

PREDICTIONS = {
    "C1": "RE(T_field) > 0 with 95% CI excluding 0, and p<0.05 in >= 1/2 counted held-out units",
    "C2": "RE(T_field S-a) CI includes 0 and point <= 0.25 x RE(raw); two-room units: y2 S-a b_room p<0.05 in >= 1/2, "
          "y2 S-a b_lab p<0.05 in <= 1/3",
    "C3": "median over {Anthropic, OpenAI, Google} cos(h_f^explore, h_f^holdout) >= 0.5 and fixed-regrouping p < 0.05",
    "C4": "T_field on agents' mean style-feature vectors p<0.05 in >= 2/3 counted held-out units",
    "C5": "RE(delta_talk) CI includes 0 and |mu|<0.05; RE(delta_content) CI includes 0 and |mu|<0.03; "
          "room-adjusted talk b_lab n.s. in all but at most one two-room held-out unit",
    "C6": "two-room units: b_room > b_lab for y3 co-movement in >= 2/3, and RE(b_room y3) > 0 (CI excludes 0)",
    "overall": "CONFIRMED if C1, C2, C3, C5 pass; REFUTED if C1 RE CI includes 0, or S-a RE > 0 with CI excluding 0, "
               "or family coupling (talk or content RE) > 0 with CI excluding 0; else INCONCLUSIVE",
}


def card_hash():
    t = CARD.read_text()
    m = re.search(r"### Confirmatory predictions for the locked holdout.*?(?=\n## )", t, flags=re.S)
    return hashlib.sha256((m.group(0) if m else "").encode()).hexdigest()[:16]


def room_rule(base, meta, u, lab_of):
    ad = pl.read_parquet(base / meta[u]["gdir"] / f"u{u}_agent_day.parquet")
    ags, H, _ = E.content_fields(ad, np.load(base / meta[u]["gdir"] / f"u{u}_agent_day_raw.npy").astype(np.float64))
    rooms = E.agent_rooms(ad, ags)
    vals, cnt = np.unique(rooms[rooms >= 0], return_counts=True)
    return int((cnt >= 2).sum()) >= 2


def style_feature_T(base, meta, u, lab_of, rng, nperm=2000):
    ad = pl.read_parquet(base / meta[u]["gdir"] / f"u{u}_agent_day.parquet")
    fc = [c for c in ad.columns if c.startswith("f_")]
    g = ad.group_by("agent").agg(*[(pl.col(c) * pl.col("n")).sum() / pl.col("n").sum() for c in fc], pl.col("n").sum().alias("nn")).sort("agent")
    Vr = np.load(base / meta[u]["gdir"] / f"u{u}_agent_day_raw.npy").astype(np.float64)
    ags, _, _ = E.content_fields(ad, Vr)
    g = g.filter(pl.col("agent").is_in(ags.tolist())).sort("agent")
    F = np.nan_to_num(g.select(fc).to_numpy().astype(float))
    F = (F - F.mean(0)) / np.where(F.std(0) > 0, F.std(0), 1)
    a = g["agent"].to_numpy()
    fam, multi = L.fam_labels([lab_of[x] for x in a])
    roles = meta[u].get("roles", {})
    keep = E.role_keep(a, roles) if roles else None
    return L.field_test(F, fam, len(multi), keep_pairs=keep, nperm=nperm, rng=rng, jack=False)


def explore_fields():
    Z = np.load(DATA / "agent_fields_explore.npz")
    meta = json.loads((DATA / "units.json").read_text())
    out = []
    for u in E.COUNTED:
        if meta[u]["regime"] != "III":
            continue
        A = Z[f"u{u}"]
        out.append({int(r[0]): np.array(r[1:]) for r in A})
    return out


def run(units, base, allow_holdout, tag):
    t0 = time.time()
    rng = np.random.default_rng(20261006)
    lab_of, name_of = E.roster()
    meta = B.build_units(units, base, allow_holdout=allow_holdout, tag=tag)
    counted = [u for u in units if len(meta[u]["days"]) >= 3]
    two = {u for u in units if room_rule(base, meta, u, lab_of)}
    # point explore.run_unit at the held-out designations (module globals read at call time)
    E.COUNTED = counted
    E.TWO_ROOM = two
    E.ONE_ROOM = set(units) - two
    E.EXCLUDE_B = {}
    res = {}
    for u in units:
        r = E.run_unit(meta, u, lab_of, rng, base=base)
        # S-a room check on two-room units
        if u in two:
            ad = pl.read_parquet(base / meta[u]["gdir"] / f"u{u}_agent_day.parquet")
            ags = np.array(sorted(int(a) for a in r["_Hs"]))
            Hs = np.array([r["_Hs"][a] for a in ags])
            fam, multi = L.fam_labels([lab_of[a] for a in ags])
            rooms = E.agent_rooms(ad, ags)
            r["c"]["y2_field_style"] = L.famroom(L.unit(Hs) @ L.unit(Hs).T, fam, rooms, len(multi), nperm=E.NP, rng=rng, jack=False)
        r["style_features_T"] = style_feature_T(base, meta, u, lab_of, rng)
        res[u] = r
    # C3 transfer
    ex = explore_fields()
    ho = [{int(a): np.array(v) for a, v in res[u]["_H"].items()} for u in counted if meta[u]["regime"] == "III"]
    tr = L.invariance(ex + ho, lab_of, E.BIG3, nperm=E.NP, rng=rng, A=list(range(len(ex))), B=list(range(len(ex), len(ex) + len(ho))))
    S = {}
    for name, fe, fs, us in (
            ("T_field", lambda r: r["a1"]["obs"], lambda r: r["a1"]["se_jack"], counted),
            ("T_field_style", lambda r: r["a2"]["obs"], lambda r: r["a2"]["se_jack"], counted),
            ("delta_talk", lambda r: r.get("b1", {}).get("delta", np.nan), lambda r: r.get("b1", {}).get("delta_se", np.nan), counted),
            ("delta_content", lambda r: r["b2"].get("delta", np.nan), lambda r: r["b2"].get("delta_se_jack", np.nan), counted),
            ("b_room_y3", lambda r: r["c"]["y3_comove"]["b_room"], lambda r: r["c"]["y3_comove"]["se_room"], [u for u in counted if u in two])):
        S[name] = L.dl_meta([fe(res[u]) for u in us], [fs(res[u]) for u in us]); S[name]["units"] = us
    V = verdicts(res, counted, two, tr, S)
    out = {"tag": tag, "card_prediction_hash": card_hash(), "predictions": PREDICTIONS, "verdicts": V, "transfer": tr, "meta": S,
           "designation": {"counted": counted, "two_room": sorted(two)},
           "units": {u: {k: v for k, v in r.items() if not k.startswith("_")} for u, r in res.items()},
           "run_at": dt.datetime.now(dt.timezone.utc).isoformat(), "seconds": round(time.time() - t0, 1)}
    (base / f"confirm_{tag}.json").write_text(json.dumps(E.clean(out), indent=1))
    print(json.dumps(E.clean(V), indent=1))
    return out


def verdicts(res, counted, two, tr, S):
    V = {}
    n = len(counted)
    t2 = [u for u in counted if u in two]
    s1 = sum(res[u]["a1"]["p"] < 0.05 for u in counted)
    c1 = S["T_field"].get("lo", -1) > 0 and s1 >= n / 2
    V["C1"] = {"pass": bool(c1), "n_sig": int(s1), "n": n, "re": S["T_field"]}
    sa = S["T_field_style"]
    room_keep = sum(res[u]["c"]["y2_field_style"]["p_room"] < 0.05 for u in t2)
    lab_keep = sum(res[u]["c"]["y2_field_style"]["p_lab"] < 0.05 for u in t2)
    c2 = (sa.get("lo", 1) <= 0 <= sa.get("hi", -1)) and sa.get("mu", 1) <= 0.25 * S["T_field"].get("mu", 0) \
        and (len(t2) == 0 or (room_keep >= len(t2) / 2 and lab_keep <= len(t2) / 3))
    V["C2"] = {"pass": bool(c2), "re_style": sa, "y2_style_room_sig": int(room_keep), "y2_style_lab_sig": int(lab_keep), "n_two_room": len(t2)}
    c3 = tr["family_median"] >= 0.5 and tr["p_regroup"] < 0.05
    V["C3"] = {"pass": bool(c3), "family_cos": tr["family_cos"], "median": tr["family_median"], "p_regroup": tr["p_regroup"]}
    s4 = sum(res[u]["style_features_T"]["p"] < 0.05 for u in counted)
    V["C4"] = {"pass": bool(s4 >= 2 * n / 3), "n_sig": int(s4), "n": n}
    dt_, dc = S["delta_talk"], S["delta_content"]
    bl = sum(res[u]["c"]["y1_talk"]["p_lab"] < 0.05 for u in t2 if "y1_talk" in res[u]["c"])
    c5 = (dt_.get("lo", 1) <= 0 <= dt_.get("hi", -1)) and abs(dt_.get("mu", 1)) < 0.05 and \
         (dc.get("lo", 1) <= 0 <= dc.get("hi", -1)) and abs(dc.get("mu", 1)) < 0.03 and bl <= 1
    V["C5"] = {"pass": bool(c5), "re_talk": dt_, "re_content": dc, "two_room_b_lab_talk_sig": int(bl)}
    y3 = sum(res[u]["c"]["y3_comove"]["b_room"] > res[u]["c"]["y3_comove"]["b_lab"] for u in t2)
    c6 = len(t2) > 0 and y3 >= 2 * len(t2) / 3 and S["b_room_y3"].get("lo", -1) > 0
    V["C6"] = {"pass": bool(c6), "room_gt_lab": int(y3), "n_two_room": len(t2), "re_b_room_y3": S["b_room_y3"]}
    refuted = (S["T_field"].get("lo", -1) <= 0) or (sa.get("lo", -1) > 0) or (dt_.get("lo", -1) > 0) or (dc.get("lo", -1) > 0)
    if c1 and c2 and c3 and c5:
        V["overall"] = "CONFIRMED"
    elif refuted:
        V["overall"] = "REFUTED"
    else:
        V["overall"] = "INCONCLUSIVE"
    return V


def main():
    if "--dry-run" in sys.argv:
        print("DRY RUN on non-holdout stand-ins:", list(DRYRUN_UNITS))
        run(DRYRUN_UNITS, DATA / "confirm_dryrun", allow_holdout=False, tag="dryrun")
        return
    if not ("--confirm" in sys.argv and "--i-understand-this-uses-the-locked-holdout" in sys.argv):
        sys.exit("Refusing to run: this script reads the LOCKED HOLDOUT. Pass --dry-run to test on non-holdout stand-ins, or "
                 "--confirm --i-understand-this-uses-the-locked-holdout (only after sign-off).")
    run(HOLDOUT_UNITS, DATA / "confirm", allow_holdout=True, tag="holdout")


if __name__ == "__main__":
    main()
