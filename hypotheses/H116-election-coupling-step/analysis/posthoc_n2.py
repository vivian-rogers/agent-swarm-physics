"""H116 post hoc (labelled): N2 re-election step against placebos at the re-election's own offsets (untrimmed, A0
windows), instead of the event's offsets. Written 2026-10-04 after seeing N2 fail against event-offset placebos.
  uv run python hypotheses/H116-election-coupling-step/analysis/posthoc_n2.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h116lib as L  # noqa: E402
import synthetic as SY  # noqa: E402

LAM = float(json.loads((L.DATA / "synthetic" / "amendment_A1.json").read_text())["lambda"])


def main():
    SY._init()
    ws_r = L.win_start(L.RE_DAY)
    off_g, off_T = L.T2_G - ws_r, L.T2 - ws_r
    vals = []
    for p in SY.PERIODS:
        calls, XR, XP, agents = SY._G[p]
        for day in sorted(calls["pt_date"].unique().to_list()):
            if day in SY.EXCLUDE_DAYS:
                continue
            ws = L.win_start(day)
            r = L.windows_at(calls, day, ws + off_T, ws + off_g, t0=ws, trim=False)
            if r is None:
                continue
            pre, post, _ = r
            a = calls["agent"].to_numpy()
            if ((a == L.WINNER) & pre).sum() < 20 or ((a == L.WINNER) & post).sum() < 20:
                continue
            f = L.fit_event(calls, XR, XP, agents, L.WINNER, pre, post, LAM, se=False)
            if f is not None:
                vals.append({"period": p, "day": day, "dJout": f["coef"]["dJout"]})
    calls, XR, XP, agents = SY._G["G26"]
    pre, post, tw = L.windows_at(calls, L.RE_DAY, L.T2, L.T2_G, t0=ws_r, trim=False)
    f = L.fit_event(calls, XR, XP, agents, L.WINNER, pre, post, LAM, se=True)
    v = np.array([x["dJout"] for x in vals])
    out = {"obs": f["coef"]["dJout"], "se": f["se"]["dJout"], "n_placebos": len(v),
           "q05": float(np.percentile(v, 5)), "q95": float(np.percentile(v, 95)), "pct": float((v < f["coef"]["dJout"]).mean()),
           "placebos": vals, "post_hoc": True}
    (L.DATA / "G26" / "posthoc_n2.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("obs", "se", "n_placebos", "q05", "q95", "pct")}))


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------- post hoc: field-only skeleton null for the 01-09 day
_K = {}


def _skel_init():
    calls, XR, XP, agents = L.load("G26")
    pre, post, _ = L.windows_at(calls, L.RE_DAY, L.T2, L.T2_G, t0=L.win_start(L.RE_DAY), trim=False)
    s = calls["s"].to_numpy()
    a = calls["agent"].to_numpy()
    md = calls["mode"].to_numpy()
    side = np.where(pre, "pre", np.where(post, "post", "out"))
    keys = np.char.add(np.char.add(a.astype(str), "|"), np.char.add(side, np.char.add("|", md.astype(str))))
    h = np.zeros(calls.height)
    for k in np.unique(keys):
        sel = keys == k
        p = ((s[sel] > 0).sum() + 0.5) / (sel.sum() + 1.0)
        h[sel] = 0.5 * np.log(p / (1 - p))
    _K.update(calls=calls, agents=agents, h=h, pre=pre, post=post)


def skel_world(seed):
    if not _K:
        _skel_init()
    A = len(_K["agents"])
    Z = np.zeros((A, A))
    s, XRs, XPs = L.CS.simulate(_K["calls"], _K["agents"], _K["h"], lambda k: Z, np.zeros(A), seed=seed)
    f = L.fit_event(_K["calls"], XRs, XPs, _K["agents"], L.WINNER, _K["pre"], _K["post"], LAM, se=False, s_override=s)
    return f["coef"]["dJout"]


def skeleton():
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=2, initializer=_skel_init) as ex:
        sk = np.array(list(ex.map(skel_world, range(21000, 21200), chunksize=8)))
    out = json.loads((L.DATA / "G26" / "posthoc_n2.json").read_text())
    out["skeleton_q95"] = float(np.percentile(sk, 95))
    out["skeleton_mean"] = float(sk.mean())
    out["pct_skeleton"] = float((sk < out["obs"]).mean())
    (L.DATA / "G26" / "posthoc_n2.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("skeleton_q95", "skeleton_mean", "pct_skeleton")}))
