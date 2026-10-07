"""Rooms are spontaneous domains (H100): the content split of #best/#rest per period, and its direction across goals.

    uv run python writeup/figures-js/export/h100_rooms.py

(a) Cartoon: two-block soft-spin model with and without a room field (the old make.py's panel_sim, same seed).
(b) Relabel excess Q_spont per regime-III period (member constants and measured field directions removed; bge,
    style-residualized) with the room-relabel null's empirical 95th percentile; filled where p_spont < 0.05.
(c) Remanence R = cos(Delta_P, Delta_P') of the spontaneous split between consecutive periods, against the joint-relabel
    null (mean +- 2 sd, from H100's stored z and null sd; all six |z| < 2).
Numbers are H100's stored results (raw_bge_small_style_resid.json). The Q null's 95th percentile is not stored, so
its relabel draws are re-run with H100's own functions and seed (h100lib.relabel_null, seed P+3, as in decompose), and
the re-run Q_spont and p_spont are asserted equal to the stored ones before the percentile is used. Reserved data: H100's agent-day table
has no reserved rows (asserted with infra/shared/common.py holdout_mask).
"""
from __future__ import annotations

import importlib.util
import json
import sys

import numpy as np
import polars as pl

from common import ROOT, write

H = ROOT / "hypotheses/H100-room-symmetry-breaking/analysis"
sys.path.insert(0, str(H))
import h100lib as L  # noqa: E402

PER = [36, 37, 38, 39, 41, 42, 44]                 # regime-III two-room periods (non-reserved)
PAIRS = [(36, 37), (37, 38), (38, 39), (39, 41), (41, 42), (42, 44)]


def holdout_mask():
    spec = importlib.util.spec_from_file_location("shared_common", ROOT / "infra/shared/common.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.holdout_mask


def sim():
    """Old make.py panel_sim, same RNG sequence: rows explicit (field h) / spontaneous; three goals each."""
    rng = np.random.default_rng(7)
    h = np.array([1.0, 0.25]); h /= np.linalg.norm(h)
    thetas = [0.6, 2.6, 4.4]
    out = []
    for row in range(2):
        for g in range(3):
            ang = np.arctan2(h[1], h[0]) + rng.normal(0, 0.12) if row == 0 else thetas[g]
            d = 0.9 * np.array([np.cos(ang), np.sin(ang)])
            pts = {}
            for r, sgn in (("best", 0.5), ("rest", -0.5)):
                pts[r] = (sgn * d + rng.normal(0, 0.28, (7, 2))).tolist()
            out.append(dict(row=row, goal=g, d=d.tolist(), **pts))
    return dict(h=h.tolist(), frames=out)


def main():
    raw = json.loads((L.DATA / "results/raw_bge_small_style_resid.json").read_text())
    tab, X = L.load("bge_small", "style_resid")
    assert not any(holdout_mask()(tab["pt_date"].to_list(), tab["goal_no"].to_list())), "reserved rows in H100 table"
    Xc = L.day_center(tab, X)
    fields = pl.read_parquet(L.DATA / "fields.parquet")
    F = np.load(L.DATA / "fields_bge_small.npy")

    per = []
    for P in PER:
        v = raw["periods"][f"G{P}"]
        ap = L.agent_period(tab, Xc, P)
        agents, H1, H2, lab = L._halves(ap)
        assert agents == v["agents"]
        A, _ = L.constants(tab, Xc, exclude={P})
        Ahat = np.array([A.get(a, np.zeros(Xc.shape[1])) for a in agents])
        E, _ = L.field_basis(fields, F, P)
        R1, R2 = L.remove_dirs(H1 - Ahat, E), L.remove_dirs(H2 - Ahat, E)
        S, _, _ = L.S_stat(R1, R2, lab)
        nul = L.relabel_null(R1, R2, lab, 2000, np.random.default_rng(P + 3))
        mu = nul.mean()
        q = dict(Q=S / mu, p=(1 + (nul >= S).sum()) / 2001)
        assert abs(q["Q"] - v["Q_spont"]) < 1e-9 and abs(q["p"] - v["p_spont"]) < 1e-12, (P, q, v["Q_spont"], v["p_spont"])
        per.append(dict(period=P, Q=v["Q_spont"], p=v["p_spont"], null95=float(np.percentile(nul, 95) / mu),
                        null50=float(np.median(nul) / mu), fielded=P in L.FIELDED, n=len(agents)))

    rem = []
    for a, b in PAIRS:
        r = raw["remanence"][f"{a}-{b}"]
        mu = r["R"] - r["z"] * r["null_sd"]          # null mean, from H100's stored z and sd
        rem.append(dict(P1=a, P2=b, R=r["R"], z=r["z"], p_two=r["p_two"], mean=mu, lo=mu - 2 * r["null_sd"],
                        hi=mu + 2 * r["null_sd"], merge=(a, b) == (39, 41)))

    sig = [d for d in per if d["p"] < 0.05]
    assert len(sig) == 5 and len(per) == 7, "paper: 5 of 7 regime-III periods"
    assert f"{min(d['Q'] for d in sig):.1f}" == "1.8" and f"{max(d['Q'] for d in sig):.1f}" == "5.7"
    assert all(abs(d["z"]) < 2 for d in rem)
    for d in per:
        print(f"G{d['period']}: Q_spont {d['Q']:.2f}  null95 {d['null95']:.2f}  p {d['p']:.3f}")
    for d in rem:
        print(f"{d['P1']}->{d['P2']}: R {d['R']:+.2f}  null mean+-2sd [{d['lo']:+.2f}, {d['hi']:+.2f}]  z {d['z']:+.2f}")
    write("h100_rooms", dict(sim=sim(), periods=per, remanence=rem), "writeup/figures-js/export/h100_rooms.py",
          ["data/processed/H100-room-symmetry-breaking/results/raw_bge_small_style_resid.json",
           "data/processed/H100-room-symmetry-breaking/agent_days.parquet", "x_style_resid_bge_small.npy",
           "fields.parquet", "fields_bge_small.npy"],
          dict(model="bge_small", variant="style_resid", n_null=2000, q_null_seed="P+3"))


if __name__ == "__main__":
    main()
