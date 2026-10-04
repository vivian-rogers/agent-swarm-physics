"""H62 synthetic validation (axis F), run before any real-data channel statistic is modelled.

S1  real skeletons (G20 regime I, G38 and G41 regime III): real messages, DQ1 ledger reads and DQ2 parents; synthetic
    ideas seeded at random agent messages; adoption per talk call under four truths:
      room    p = 1 - (1 - q)^(read uses in the last 3 talk-call windows), any channel
      reply   p = 1 - (1 - q_rep)^(reply-channel read uses in the window)
      thread  p = q_tf if a reply partner posted a use in the last 300 s, read or not (thread field / convergence)
      field   no read effect
    plus a field eps per talk call in the first 24 h. Adopters re-use the marker (prob 0.2 per talk call, 1 h).
S2  shared simulator (DQ8 simulate.py, Hawkes with parents, G38 skeleton): true parents known; reply-only
    transmission on true-parent ties; estimation with true parents vs DQ2-like noisy parents (keep 0.5, wrong 0.07).
  uv run python hypotheses/H62-ideas-travel-reply-graph/analysis/synthetic.py [--s1] [--s2]
Output: data/processed/H62-ideas-travel-reply-graph/synthetic/{s1.parquet,s2.parquet,summary.json}
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_v] = "1"

import json  # noqa: E402
import sys  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h62core as C  # noqa: E402
import h62lib as L  # noqa: E402

OUT = ROOT / "data/processed/H62-ideas-travel-reply-graph"
TRUTHS = {"room": dict(q=0.004), "reply": dict(q=0.010), "thread": dict(q=0.012), "field": dict(q=0.0)}
EPS = 0.002
N_IDEAS = 1000
_P = {}


def period(g: int) -> dict:
    if g not in _P:
        import idea_ledger as IL
        P = IL.load_period(IL.Base(), g, with_markers=False)
        _P[g] = P
    return _P[g]


def sim_ideas(P: dict, truth: str, rng, ties=None, n_ideas: int = N_IDEAS):
    t, kind, sender, TS, cs, par = P["t"], P["kind"], P["sender"], P["TS"], P["cs"], P["parent"]
    ties = C.reply_ties(P) if ties is None else ties
    ag = np.where((kind == 0) & (sender >= 0) & ~np.isin(sender, list(P["cc"])))[0]
    # s_back per agent message: producing-call start of the agent's 3rd-previous talk call
    sback = np.full(len(t), np.iinfo(np.int64).min // 2, dtype=np.int64)
    for a in np.unique(sender[ag]):
        xa = ag[sender[ag] == a]
        sa = cs[xa]
        sb = np.r_[np.full(C.MEM_TURNS, np.iinfo(np.int64).min // 2), sa][: len(sa)]
        sback[xa] = sb
    q = TRUTHS[truth]["q"]
    seeds = rng.choice(ag, n_ideas, replace=False)
    use_pos, use_mk = [], []
    for i, s0 in enumerate(np.sort(seeds)):
        t0 = t[s0]
        uses = [int(s0)]
        used = {int(sender[s0]): t0}
        lo = np.searchsorted(t[ag], t0, side="right")
        hi = np.searchsorted(t[ag], t0 + C.DAY_US, side="right")
        for x in ag[lo:hi]:
            j = int(sender[x])
            if j in used:
                if t[x] - used[j] <= 3600 * C.US and rng.random() < 0.2:
                    uses.append(int(x))
                continue
            up = np.array(uses)
            oth = sender[up] != j
            up = up[oth]
            p = 0.0
            if len(up):
                tsj = TS[up, j]
                rec = (tsj <= cs[x]) & (tsj > sback[x])
                if truth == "room":
                    p = 1 - (1 - q) ** int(rec.sum())
                elif truth in ("reply", "thread"):
                    rep = np.zeros(len(up), bool)
                    for k_, u in enumerate(up):
                        k = int(sender[u])
                        dr = par[u] >= 0 and kind[par[u]] == 0 and sender[par[u]] == j
                        rep[k_] = dr or C._tie(ties, k, j, np.array([t[u] - C.TIE_US]), np.array([t[u]]))[0]
                    if truth == "reply":
                        p = 1 - (1 - q) ** int((rec & rep).sum())
                    else:
                        p = q if (rep & (t[up] > t[x] - C.LAG5)).any() else 0.0
            p = 1 - (1 - p) * (1 - EPS)
            if rng.random() < p:
                uses.append(int(x))
                used[j] = t[x]
        use_pos += uses
        use_mk += [i + 1] * len(uses)
    return np.array(use_pos, np.int64), np.array(use_mk, np.int64), np.full(len(use_pos), 2, np.int8)


def estimate(P: dict, B: int = 100, seed: int = 0) -> dict:
    r = C.assemble(P, cap=10 ** 6)
    a = L.hr_fit(r["cells"], L.MODEL_A, B=B, seed=seed, contrasts={"Lam": ("rec_rep", "rec_room")})
    b = L.hr_fit(r["cells"], L.MODEL_B, B=0, seed=seed, contrasts={"C_rep": ("s_rep5", "u_rep5x"),
                                                                  "C_room": ("s_room5", "u_room5x")})
    t = L.transmissibility(r["events"], B=300, seed=seed)
    out = dict(n_adopt=a.get("n_adopt"), Lam=a.get("Lam"), Lam_lo=a.get("Lam_lo"), Lam_hi=a.get("Lam_hi"),
               hr_rep=a.get("hr_rec_rep"), hr_room=a.get("hr_rec_room"),
               C_rep=b.get("C_rep"), C_rep_lo=b.get("C_rep_wlo"), C_rep_hi=b.get("C_rep_whi"),
               C_room=b.get("C_room"), C_room_lo=b.get("C_room_wlo"), C_room_hi=b.get("C_room_whi"),
               T_ratio=t.get("T_ratio"), T_lo=t.get("T_ratio_lo"), T_hi=t.get("T_ratio_hi"))
    out.update(L.branching(r["adopters"]))
    return out


def run_s1(args):
    g, truth, rep = args
    P = dict(period(g))
    rng = np.random.default_rng(10000 * g + 100 * list(TRUTHS).index(truth) + rep)
    up, um, uc = sim_ideas(P, truth, rng)
    P.update(use_pos=up, use_marker=um, use_cls=uc)
    return dict(goal=g, truth=truth, rep=rep, **estimate(P, seed=rep))


# ------------------------------------------------------------------------------------------- S2: shared simulator
def sim_world(unit: str, seed: int):
    import simulate as SIM
    sk = SIM.extract_skeleton(unit)
    sim = SIM.simulate(sk, seed=seed, **SIM.preset("hawkes", n_x=0.3, n_s=0.2))
    tb = sim.tables()
    ch = tb["chat_core"].join(tb["msg_truth"], on="message_id").sort("t")
    # parent_msg indexes the pre-sort order: map through message ids
    ids_presort = tb["msg_truth"]["message_id"].to_list()
    pos_of = {m: i for i, m in enumerate(ch["message_id"].to_list())}
    tpar = np.full(ch.height, -1, np.int64)
    for m, pm in zip(ch["message_id"].to_list(), ch["parent_msg"].to_list()):
        if pm is not None and pm >= 0:
            tpar[pos_of[m]] = pos_of[ids_presort[pm]]
    t = ch["t"].dt.epoch("us").to_numpy().astype(np.int64)
    sender = ch["agent"].to_numpy().astype(np.int16)
    room = ch["room"].to_numpy().astype(np.int16)
    cw = tb["call_windows"]
    n_ag = int(max(sender.max(), cw["agent"].max())) + 1
    calls = {int(a): np.sort(cw.filter(pl.col("agent") == a)["t_call"].dt.epoch("us").to_numpy().astype(np.int64))
             for a in cw["agent"].unique().to_list()}
    # read-out: recipient a reads m at its first call after t_m if a posted in m's room that day (same-day presence)
    day = (t // (24 * 3600 * C.US)).astype(np.int64)
    pres = {}
    for a_, r_, d_ in zip(sender, room, day):
        pres.setdefault((int(r_), int(d_)), set()).add(int(a_))
    TS = np.full((len(t), n_ag), C.INF_US, np.int64)
    for m in range(len(t)):
        for a in pres.get((int(room[m]), int(day[m])), ()):
            ca = calls.get(a)
            if a == sender[m] or ca is None:
                continue
            k = np.searchsorted(ca, t[m], side="right")
            if k < len(ca):
                TS[m, a] = ca[k]
    cs = t - C.US
    for a, ca in calls.items():
        idx = np.where(sender == a)[0]
        k = np.searchsorted(ca, t[idx], side="left") - 1
        ok = k >= 0
        cs[idx[ok]] = ca[k[ok]]
    P = dict(t=t, kind=np.zeros(len(t), np.int8), sender=sender, cc=set(), TS=TS, cs=cs, parent=tpar,
             room=room, rows=np.arange(len(t)))
    return P


def noisy_parents(P: dict, rng, keep: float = 0.5, wrong: float = 0.07) -> np.ndarray:
    t, sender, room, tpar = P["t"], P["sender"], P["room"], P["parent"]
    obs = np.full(len(t), -1, np.int64)
    for m in range(len(t)):
        u = rng.random()
        if tpar[m] >= 0 and u < keep:
            obs[m] = tpar[m]
        elif u < keep + wrong:
            cand = [x for x in range(max(0, m - 6), m) if sender[x] != sender[m] and room[x] == room[m]
                    and x != tpar[m]]
            if cand:
                obs[m] = int(rng.choice(cand))
    return obs


def run_s2(args):
    unit, seed, truth = args
    P = sim_world(unit, seed)
    rng = np.random.default_rng(seed)
    ties_true = C.reply_ties(P)
    up, um, uc = sim_ideas(P, truth, rng, ties=ties_true, n_ideas=min(N_IDEAS, len(P["t"]) // 4))
    P.update(use_pos=up, use_marker=um, use_cls=uc)
    res = []
    for lab, par in (("true", P["parent"]), ("noisy", noisy_parents(P, rng))):
        Q = dict(P)
        Q["parent"] = par
        res.append(dict(unit=unit, seed=seed, truth=truth, parents=lab, n_msgs=len(P["t"]), **estimate(Q, B=60, seed=seed)))
    return res


def main():
    (OUT / "synthetic").mkdir(parents=True, exist_ok=True)
    summ = {}
    if "--s2" not in sys.argv or "--s1" in sys.argv:
        if "--reuse-s1" in sys.argv and (OUT / "synthetic/s1.parquet").exists():
            s1 = pl.read_parquet(OUT / "synthetic/s1.parquet")
        else:
            jobs = [(g, tr, r) for g in (20, 38, 41) for tr in TRUTHS for r in range(6)]
            with Pool(4) as pool:
                res = pool.map(run_s1, jobs, chunksize=1)
            s1 = pl.DataFrame(res)
            s1.write_parquet(OUT / "synthetic/s1.parquet")
        for tr in TRUTHS:
            d = s1.filter(pl.col("truth") == tr)
            summ[f"s1_{tr}"] = dict(
                n=d.height, med_Lam=float(d["Lam"].median()), rej_Lam=float((d["Lam_lo"] > 1).mean()),
                rej_Lam_low=float((d["Lam_hi"] < 1).mean()), med_T=float(d["T_ratio"].median()),
                rej_T=float((d["T_lo"] > 1).mean()), med_C_rep=float(d["C_rep"].median()),
                rej_C_rep=float((d["C_rep_lo"] > 1).mean()), med_C_room=float(d["C_room"].median()),
                rej_C_room=float((d["C_room_lo"] > 1).mean()), med_adopt=float(d["n_adopt"].median()),
                med_R=float(d["R_hat"].median()))
    if "--s1" not in sys.argv or "--s2" in sys.argv:
        jobs = [("38a", s, tr) for s in range(4) for tr in ("reply", "room")]
        with Pool(4) as pool:
            res = pool.map(run_s2, jobs, chunksize=1)
        s2 = pl.DataFrame([x for r in res for x in r])
        s2.write_parquet(OUT / "synthetic/s2.parquet")
        for (tr, lab), d in s2.group_by(["truth", "parents"]):
            summ[f"s2_{tr}_{lab}"] = dict(n=d.height, med_Lam=float(d["Lam"].median()),
                                          rej_Lam=float((d["Lam_lo"] > 1).mean()), med_T=float(d["T_ratio"].median()),
                                          med_adopt=float(d["n_adopt"].median()))
    old = json.loads((OUT / "synthetic/summary.json").read_text()) if (OUT / "synthetic/summary.json").exists() else {}
    old.update(summ)
    (OUT / "synthetic/summary.json").write_text(json.dumps(old, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
