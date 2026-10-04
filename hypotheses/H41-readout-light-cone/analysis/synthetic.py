"""H41 synthetic validation (axis F): planted spreading on real call schedules and read-out graphs.

  uv run python hypotheses/H41-readout-light-cone/analysis/synthetic.py [--reps 4] [--items 400] [--skel 38,31,51]

Truths (card, "Synthetic validation plan"):
  T1 relay        hazard q per talk message from the item-exposure call on (q = 0.05, 0.15), field eps0 = 0.001
  T2 field        pulse eps(t) = p0 exp(-(t - t_on)/600 s), onset U(0, 300 s) before t0, + eps0; no relay
  T3 hidden       T1 (q = 0.15) + a hidden channel (other-room agents: exposure at t0 + Exp(30 min); #31: two agent
                  pairs with an instant channel)
  T4 timing       T1 (q = 0.15) with generative call starts drawn in [t_call_lo, t_call_hi]; analysis uses the ledger
The synthetic uses are run through the same `scheme/build.py: analyze` as the real data.
Outputs: data/processed/H41-readout-light-cone/synthetic/{runs.parquet, summary.json}
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(HERE))
import h41core as C  # noqa: E402
import build as BLD  # noqa: E402
import h41stats as S  # noqa: E402

OUTD = C.OUT / "synthetic"
HORIZON = 6 * 3600.0
EPS0 = 0.001


def skeleton(name: str, cal):
    if name == "38":
        return C.load_skeleton(38, cal)
    if name == "31":
        return C.load_skeleton(31, cal)
    if name == "51":
        return C.load_skeleton(51, cal, days_filter=lambda d: "2026-07-06" <= d <= "2026-07-23")
    raise ValueError(name)


class Sim:
    def __init__(self, sk: C.Skeleton, ri: C.RoomIndex, rng):
        self.sk, self.ri, self.rng = sk, ri, rng
        m = sk.msgs.filter((pl.col("kind") == "agent") & pl.col("ci_talk").is_not_null()
                           & pl.col("agent").is_in(list(map(int, sk.agents))))
        m = m.sort("t", "mrow")
        self.tt = m["t"].to_numpy()
        self.ta = m["agent"].to_numpy().astype(int)
        self.tci = m["ci_talk"].to_numpy().astype(int)
        self.tm = m["mrow"].to_numpy().astype(int)
        self.readers = {k: (sk.e_reader[v], sk.e_ci[v]) for k, v in sk.readers_of.items()}
        self.readers_true = self.readers
        # two most active agents pairs for the #31 instant channel
        cnt = np.bincount(self.ta, minlength=64)
        top = np.argsort(-cnt)[:4]
        self.pairs = {int(top[0]): int(top[1]), int(top[1]): int(top[0]), int(top[2]): int(top[3]), int(top[3]): int(top[2])}

    def perturb_timing(self):
        """Generative call starts uniform in [lo, hi], monotone per agent, before the call's first record."""
        sk = self.sk
        tt = self.rng.uniform(sk.c_lo, np.maximum(sk.c_hi, sk.c_lo))
        tt = np.minimum(tt, sk.c_first - 0.05)
        for a, s in sk.agent_calls.items():
            tt[s] = np.maximum.accumulate(tt[s])
        self.t_true = tt
        rd = {}
        for k, v in sk.readers_of.items():
            r = sk.e_reader[v]
            tm = sk.e_tm[v]
            cis = np.empty(len(v), np.int64)
            for j, (a, t_m) in enumerate(zip(r, tm)):
                s = sk.agent_calls[int(a)]
                cis[j] = np.searchsorted(tt[s], t_m, side="right")
            rd[k] = (r, cis)
        self.readers_true = rd

    def call_after(self, a, t):
        s = self.sk.agent_calls[int(a)]
        return int(np.searchsorted(self.sk.c_t[s], t, side="right"))

    def call_containing(self, a, t):
        s = self.sk.agent_calls[int(a)]
        return int(max(np.searchsorted(self.sk.c_t[s], t, side="right") - 1, 0))

    def run_item(self, m0, truth, q, hidden_mode=None, p0=0.10):
        """Simulate one item seeded at message row m0; returns (uses mrows, causes per adopter)."""
        sk, rng = self.sk, self.rng
        t0 = float(sk.msgs["t"][m0])
        src = int(sk.msgs["agent"][m0])
        lo = np.searchsorted(self.tt, t0, side="right")
        hi = np.searchsorted(self.tt, t0 + HORIZON, side="right")
        exp_ci = {"src": {}, "field": {}, "hidden": {}}   # logged item exposure by lineage of the carrier
        hid_ci = {}
        adopted = {src}
        lineage = {src: "src"}
        uses = [m0]
        causes = {}
        rd = self.readers_true

        def add_carrier(mr, lin):
            v = rd.get(int(mr))
            if v is None:
                return
            d = exp_ci[lin]
            for r, c in zip(v[0], v[1]):
                r = int(r)
                if c < d.get(r, 10**12):
                    d[r] = int(c)

        add_carrier(m0, "src")
        room0 = int(sk.msgs["room"][m0])
        if truth == "T3":
            if hidden_mode == "pairs":
                if src in self.pairs:  # shared private access (e.g. both read the same file) up to 10 min before t0
                    b = self.pairs[src]
                    hid_ci[b] = self.call_containing(b, t0 - rng.uniform(0, 600))
            else:
                for a in sk.agents:
                    a = int(a)
                    if a != src and self.ri.at(a, t0) != room0:
                        th = t0 + rng.exponential(1800.0)
                        hid_ci[a] = self.call_after(a, th)
        t_on = t0 - rng.uniform(0, 300)
        BIG = 10**12
        for k in range(lo, hi):
            a = int(self.ta[k])
            ci = int(self.tci[k])
            t = float(self.tt[k])
            if a in adopted:
                if a != src and rng.random() < 0.3:  # re-use carries the item further
                    uses.append(int(self.tm[k]))
                    add_carrier(self.tm[k], lineage[a])
                continue
            f = EPS0
            if truth == "T2":
                f += p0 * np.exp(-(t - t_on) / 600.0)
            e_src = exp_ci["src"].get(a, BIG) <= ci
            e_oth = (exp_ci["field"].get(a, BIG) <= ci) or (exp_ci["hidden"].get(a, BIG) <= ci)
            rel = q if (truth != "T2" and (e_src or e_oth)) else 0.0
            if truth == "T1d" and rel > 0:  # relay hazard decays with time since the first exposing read
                cmin = min(exp_ci["src"].get(a, BIG), exp_ci["field"].get(a, BIG), exp_ci["hidden"].get(a, BIG))
                t_exp = self.sk.c_t[self.sk.agent_calls[a]][cmin]
                rel = q * np.exp(-max(t - t_exp, 0.0) / 600.0)
            hid = q if (truth == "T3" and hid_ci.get(a, BIG) <= ci and rel == 0.0) else 0.0
            lam = 1 - (1 - f) * (1 - rel) * (1 - hid)
            if rng.random() < lam:
                comp = np.array([f, rel, hid])
                cause = ["field", "relay", "hidden"][int(rng.choice(3, p=comp / comp.sum()))]
                if cause == "relay":
                    lin = "src" if e_src else ("hidden" if exp_ci["hidden"].get(a, BIG) <= ci else "field")
                else:
                    lin = cause
                adopted.add(a)
                lineage[a] = lin
                uses.append(int(self.tm[k]))
                causes[a] = (cause, lin)
                add_carrier(self.tm[k], lin)
                if truth == "T3" and hidden_mode == "pairs" and a in self.pairs:
                    b = self.pairs[a]
                    if b not in adopted:
                        hid_ci[b] = min(hid_ci.get(b, BIG), self.call_containing(b, t - rng.uniform(0, 600)))
        return uses, causes


def _fm(x):
    return float(x.mean()) if len(x) else float("nan")


def run(skname, reps, n_items, seed0=0):
    cal = C.calendar()
    sk = skeleton(skname, cal)
    ri = C.RoomIndex(sk)
    rows = []
    msgs = sk.msgs
    cand = msgs.filter((pl.col("kind") == "agent") & pl.col("ci_talk").is_not_null()
                       & pl.col("agent").is_in(list(map(int, sk.agents))) & (pl.col("t") < sk.t_max - HORIZON))
    cand_rows = cand["mrow"].to_numpy()
    configs = [("T1", 0.05), ("T1", 0.15), ("T1d", 0.4), ("T2", 0.0), ("T3", 0.15), ("T4", 0.15)]
    hidden_mode = "pairs" if skname == "31" else "rooms"
    for rep in range(reps):
        for truth, q in configs:
            rng = np.random.default_rng(1000 * seed0 + 100 * rep + hash((skname, truth, q)) % 97)
            sim = Sim(sk, ri, rng)
            if truth == "T4":
                sim.perturb_timing()
            seeds = rng.choice(cand_rows, size=min(n_items, len(cand_rows)), replace=False)
            urows, causes_all = [], []
            for j, m0 in enumerate(seeds):
                mk = -(j + 1)
                uses, causes = sim.run_item(int(m0), truth, q, hidden_mode)
                for mr in uses:
                    urows.append((mk, mr))
                for a, c in causes.items():
                    causes_all.append((mk, a, c[0], c[1]))
            u = (pl.DataFrame({"marker": [r[0] for r in urows], "mrow": [r[1] for r in urows]},
                              schema={"marker": pl.Int64, "mrow": pl.Int64})
                 .unique(["marker", "mrow"])
                 .join(msgs.select("message_id", "mrow", "t", "room", "kind", "agent", "node", "ci_talk", "pt_date")
                       .with_columns(pl.col("mrow").cast(pl.Int64)), on="mrow", how="inner")
                 .sort("marker", "t", "mrow"))
            nov = pl.DataFrame({"marker": np.arange(-len(seeds), 0, dtype=np.int64), "cls": np.full(len(seeds), 2, np.uint8)})
            t_a = time.time()
            items, adf, hz, _ = BLD.analyze(sk, u, nov, cal, ri)
            cz = pl.DataFrame({"marker": [c[0] for c in causes_all], "agent": [c[1] for c in causes_all],
                               "cause": [c[2] for c in causes_all], "lineage": [c[3] for c in causes_all]},
                              schema={"marker": pl.Int64, "agent": pl.Int64, "cause": pl.Utf8, "lineage": pl.Utf8})
            if adf.height == 0:
                continue
            adf = adf.with_columns(pl.col("agent").cast(pl.Int64)).join(cz, on=["marker", "agent"], how="left")
            vs = S.violation_shares(adf, B=200, seed=rep)
            hj = S.hazard_jump(hz, B=300, seed=rep)
            ve = S.velocity(adf)
            hm = S.hazard_jump_mh(hz, B=200, seed=rep)
            hml = S.hazard_jump_mh(hz, B=200, seed=rep, prefix="L_")
            rel = adf.filter((pl.col("cause") == "relay") & (pl.col("lineage") == "src"))
            hid = adf.filter(pl.col("cause") == "hidden")
            desc = adf.filter(pl.col("lineage") != "src")  # field/hidden adopters and their relay descendants
            hid_pre = hid.filter((pl.col("K") < 0) | (pl.col("ci_use") < pl.col("K")))
            row = dict(skel=skname, rep=rep, truth=truth, q=q, n_items=len(seeds), n_adopt=adf.height,
                       A=vs["acaus"], A_rob=vs["acaus_rob"], A_early=vs["acaus_early"], A_jit=vs["p_jit"],
                       A_jit_early=vs["p_jit_early"], V4=vs["v4"], V4_inf=vs["v4_hinf"], A_room=vs["out_room"],
                       diff_early_lo=vs["diff_early_ci"][0], diff_early_hi=vs["diff_early_ci"][1],
                       A_relay=float((~rel["in_cone"]).mean()) if rel.height else np.nan,
                       A_rob_relay=float((~rel["in_cone_len"]).mean()) if rel.height else np.nan,
                       n_relay=rel.height, n_hidden=hid.height,
                       hid_flag=float((~hid["in_cone"]).mean()) if hid.height else np.nan,
                       hid_flag_or_unexp=float(((~hid["in_cone"]) | (~hid["exposed"])).mean()) if hid.height else np.nan,
                       hid_pre_flag=float((~hid_pre["in_cone"]).mean()) if hid_pre.height else np.nan,
                       n_hid_pre=hid_pre.height,
                       nonhid_flag=float((~adf.filter(pl.col("cause") != "hidden")["in_cone"]).mean()),
                       srcline_flag=_fm(~adf.filter(pl.col("lineage") == "src")["in_cone"]),
                       desc_flag=float((~desc["in_cone"]).mean()) if desc.height else np.nan, n_desc=desc.height,
                       J_mh=hm.get("J_mh"), J_mh_lo=hm.get("J_mh_ci", (np.nan, np.nan))[0],
                       J_mh_hi=hm.get("J_mh_ci", (np.nan, np.nan))[1], J_mh_len=hml.get("J_mh"),
                       J_mh_len_lo=hml.get("J_mh_ci", (np.nan, np.nan))[0],
                       J_in=hj.get("J_in"), J_in_lo=hj.get("J_in_ci", (np.nan, np.nan))[0],
                       J_in_hi=hj.get("J_in_ci", (np.nan, np.nan))[1], risk_pre_in=hj.get("risk_pre_in"),
                       J=hj.get("J"), J_lo=hj.get("J_ci", (np.nan, np.nan))[0], J_hi=hj.get("J_ci", (np.nan, np.nan))[1],
                       h_pre=hj.get("h_pre"), h_o1=hj.get("h_o1"), risk_pre=hj.get("risk_pre"), adopt_o1=hj.get("adopt_o1"),
                       J_room=hj.get("J_room"), cyc_med=ve.get("cyc_med"), talk_med=ve.get("talk_med"),
                       secs=round(time.time() - t_a, 1))
            rows.append(row)
            print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=4)
    ap.add_argument("--items", type=int, default=400)
    ap.add_argument("--skel", default="38,31,51")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    allrows = []
    for s in a.skel.split(","):
        allrows += run(s, a.reps, a.items)
        df = pl.DataFrame(allrows, infer_schema_length=None)
        df.write_parquet(OUTD / f"runs{a.tag}.parquet")
    print("done")


if __name__ == "__main__":
    main()
