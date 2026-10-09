"""H148 synthetic validation (axis F) on the real #51 skeleton: W_atoms, W_field, W_nested (card "Synthetic
validation"). The skeleton is real: bins, trim, days, phase, exogenous-input bins, which agents are present in
which bins, each agent's marginal over its project states, the artifact owners and their non-owner write rates.
Everything else is simulated, so planted truth is known.

  W_atoms   independent agents (own Markov persistence) with own artifacts written from the owner's state;
            elements expressed by small host sets with per-agent persistence; rooms from activity. Truth: agents and
            agent + own artifact; no multi-agent system and no memeplex.
  W_field   W_atoms plus the fields that E holds: exogenous-input bins pull present agents to a common topic and
            express 8 field elements; first bins of the day hold agents in 'active, no touch'; element rates follow
            village activity; role classes share static vocabularies. Truth as W_atoms.
  W_nested  W_atoms plus a planted pair (two agents follow a shared latent Z with probability rho and write a
            shared artifact) inside a planted memeplex of 6 elements whose expression rises with its own prevalence
            (weight w) and with the pair's state, over changing hosts. Truth: pair, memeplex, pair + memeplex.

Usage: uv run python hypotheses/H148-agent-discovery-51/analysis/synthetic.py [--profile] [--reps 20]
       [--worlds W_atoms,W_field,W_nested] [--width 30] [--shuffle]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h148lib as L  # noqa: E402
import individuality as IND  # noqa: E402

N_EL = 100
SYN = L.OUT / "synthetic"


def skeleton(width: int):
    P = L.load_panel(width, with_elements=False)
    ag = P.agent_rows
    pres = P.present
    marg = np.zeros((ag.size, 5))
    for i, a in enumerate(ag):
        s = P.S[a][P.valid & (P.S[a] > 0)]
        c = np.bincount(s, minlength=5)[1:].astype(float) + 0.5
        marg[i, 1:] = c / c.sum()
    art = np.flatnonzero(P.kind == "artifact")
    own_row = {}
    for r in art:
        o = P.owner[r]
        w = np.flatnonzero(P.agent_of == o)
        own_row[r] = int(w[0]) if w.size else -1
    nonown = np.array([((P.S[r] == 2) & P.valid).sum() / max(P.valid.sum(), 1) for r in art])
    return P, pres, marg, art, own_row, nonown


def sim_agents(rng, P, pres, marg, p_stay=0.75):
    nA, nB = pres.shape
    X = np.zeros((nA, nB), np.int8)
    cum = marg.cumsum(1)
    for b in range(nB):
        draw = (rng.random(nA)[:, None] > cum).sum(1).astype(np.int8)
        draw = np.clip(draw, 1, 4)
        if b > 0 and P.day[b] == P.day[b - 1]:
            keep = (X[:, b - 1] > 0) & (rng.random(nA) < p_stay)
            X[:, b] = np.where(keep, X[:, b - 1], draw)
        else:
            X[:, b] = draw
        X[~pres[:, b], b] = 0
    return X


def sim_artifacts(rng, P, Xag, art, own_row, nonown, q1=0.6, q0=0.05):
    nB = Xag.shape[1]
    A = np.zeros((art.size, nB), np.int8)
    agrow = {r: i for i, r in enumerate(P.agent_rows)}
    for j, r in enumerate(art):
        o = own_row[r]
        if o >= 0:
            s = Xag[agrow[o]]
            p = np.where(s == 2, q1, np.where(s > 0, q0, 0.0))
            A[j] = (rng.random(nB) < p).astype(np.int8)
        vis = rng.random(nB) < nonown[j]
        A[j] = np.where(vis, 2, A[j])
    return A


def sim_rooms(rng, P, Xag):
    nB = Xag.shape[1]
    na = (Xag > 0).sum(0) + rng.normal(0, 2, nB)
    g = np.where((Xag > 0).sum(0) == 0, 0, np.where(na > np.median(na[P.valid]), 2, 1)).astype(np.int8)
    f = np.zeros(nB, np.int8)
    real_focus = P.S[np.flatnonzero(P.kind == "room")[1]]
    on = np.zeros(nB, bool)
    for d in np.unique(P.day):
        ix = P.day == d
        on[ix] = (real_focus[ix] > 0).any()
    for b in range(nB):
        if on[b]:
            f[b] = f[b - 1] if (b > 0 and rng.random() < 0.7 and f[b - 1] > 0) else rng.integers(1, 3)
    return np.vstack([g, f])


def sim_elements(rng, P, Xag, n_el=N_EL, rate_mult=None, hosts=None, extra=None):
    """extra(b, present, expr_prev) -> per-element-per-agent added probability (n_el, nA) or None."""
    nA, nB = Xag.shape
    pres = Xag > 0
    if hosts is None:
        hosts = np.zeros((n_el, nA))
        for e in range(n_el):
            h = rng.choice(nA, size=rng.integers(3, 9), replace=False)
            hosts[e, h] = rng.uniform(0.02, 0.15, h.size)
    S = np.zeros((n_el, nB), np.int8)
    prev = np.zeros((n_el, nA), bool)
    for b in range(nB):
        if b > 0 and P.day[b] != P.day[b - 1]:
            prev[:] = False
        p = hosts * (1.0 if rate_mult is None else rate_mult[b]) + 0.3 * prev * (hosts > 0)
        if extra is not None:
            add = extra(b, pres[:, b], prev)
            if add is not None:
                p = p + add
        p = np.clip(p, 0, 1) * pres[:, b][None, :]
        ex = rng.random((n_el, nA)) < p
        c = ex.sum(1)
        S[:, b] = np.where(c == 0, 0, np.where(c == 1, 1, 2))
        prev = ex
    return S, hosts


def make_panel(P, Xag, A, R, E, names_el, owner_override=None):
    S = np.vstack([Xag, A, R, E])
    K = np.r_[np.full(Xag.shape[0], 5), np.full(A.shape[0], 3), np.full(R.shape[0], 3), np.full(E.shape[0], 3)]
    nb = P.agent_rows.size + A.shape[0] + R.shape[0]
    kind = np.r_[P.kind[:nb], np.array(["element"] * E.shape[0], object)]
    names = list(P.names[:nb]) + names_el
    agent_of = np.r_[P.agent_of[:nb], -np.ones(E.shape[0], int)]
    owner = np.r_[P.owner[:nb], -np.ones(E.shape[0], int)].copy()
    if owner_override:
        for r, o in owner_override.items():
            owner[r] = o
    return L.Panel(S, K, kind, names, agent_of, owner, P.day, P.valid, P.phase, P.exo, P.width)


def world(name, rep, width=30, rho=0.7, w=0.4, n_el=N_EL):
    """One synthetic world on the real skeleton. n_el = 0 gives the agent-level configuration (no element atoms)."""
    rng = np.random.default_rng(1000 * rep + {"W_atoms": 1, "W_field": 2, "W_nested": 3}[name])
    P, pres, marg, art, own_row, nonown = skeleton(width)
    truth = {"planted": {}}
    Xag = sim_agents(rng, P, pres, marg)
    nA = Xag.shape[0]
    if name == "W_field":
        # common topic in and after human/relayed-input bins; start-of-day orientation (both held by E)
        ex = P.exo == 2
        exn = ex | np.r_[False, ex[:-1]]
        for b in np.flatnonzero(exn):
            m = (Xag[:, b] > 0) & (rng.random(nA) < 0.5)
            Xag[m, b] = 4
        for b in np.flatnonzero(P.phase == 0):
            m = (Xag[:, b] > 0) & (rng.random(nA) < 0.5)
            Xag[m, b] = 1
    owner_override = {}
    if name == "W_nested":
        ag = P.agent_rows
        cop = (pres[:, P.valid].astype(float) @ pres[:, P.valid].T.astype(float))
        hasown = np.array([any(own_row[r] == a for r in art) for a in ag])
        best, pair = -1, None
        for i in range(ag.size):
            for j in range(i + 1, ag.size):
                if hasown[i] and hasown[j] and cop[i, j] > best:
                    best, pair = cop[i, j], (i, j)
        i, j = pair
        Z = np.zeros(P.nB, np.int8)
        for b in range(P.nB):
            Z[b] = Z[b - 1] if (b > 0 and P.day[b] == P.day[b - 1] and rng.random() < 0.9) else rng.integers(0, 2)
        for k in (i, j):
            f = (Xag[k] > 0) & (rng.random(P.nB) < rho)
            Xag[k] = np.where(f, np.where(Z == 1, 3, 2), Xag[k]).astype(np.int8)
        shared_cands = [r for r in art if own_row[r] not in (ag[i], ag[j]) and nonown[list(art).index(r)] < 0.02]
        rp = shared_cands[0]
        own_row = dict(own_row)
        own_row[rp] = -1
        owner_override[rp] = int(P.agent_of[ag[i]])
        truth["pair_agents"] = [int(ag[i]), int(ag[j])]
    A = sim_artifacts(rng, P, Xag, art, own_row, nonown)
    if name == "W_nested":
        jr = list(art).index(rp)
        wi = (Xag[i] == 3) & (rng.random(P.nB) < 0.6)
        wj = (Xag[j] == 3) & (rng.random(P.nB) < 0.6)
        A[jr] = np.where(wj, 2, np.where(wi, 1, 0)).astype(np.int8)
        truth["planted"]["pair"] = sorted([int(ag[i]), int(ag[j]), int(rp)])
    R = sim_rooms(rng, P, Xag)
    nb = P.agent_rows.size + art.size + 2
    if n_el == 0:
        E = np.zeros((0, P.nB), np.int8)
    elif name == "W_atoms":
        E, _ = sim_elements(rng, P, Xag, n_el)
    elif name == "W_field":
        roles = rng.integers(0, 6, nA)
        hosts = np.zeros((n_el, nA))
        for e in range(8, n_el):
            h = np.flatnonzero(roles == rng.integers(0, 6))
            hosts[e, h] = rng.uniform(0.02, 0.12, h.size)
        act = (Xag > 0).sum(0).astype(float)
        mult = act / max(act[P.valid].mean(), 1e-9)
        exn = (P.exo == 2) | np.r_[False, P.exo[:-1] == 2]

        def extra(b, present, prev):
            if exn[b]:
                add = np.zeros((n_el, nA))
                add[:8] = 0.3
                return add
            return None
        E, _ = sim_elements(rng, P, Xag, n_el, rate_mult=mult, hosts=hosts, extra=extra)
        truth["field_elements"] = [int(nb + k) for k in range(8)]
    else:
        hosts = np.zeros((n_el, nA))
        for e in range(6, n_el):
            h = rng.choice(nA, size=rng.integers(3, 9), replace=False)
            hosts[e, h] = rng.uniform(0.02, 0.15, h.size)
        base = np.full(nA, 0.02)
        base[[i, j]] = 0.06
        hosts[:6] = base[None, :]

        def extra(b, present, prev):
            add = np.zeros((n_el, nA))
            m = prev[:6].any(1).mean() if b > 0 and P.day[b] == P.day[b - 1] else 0.0
            add[:6] = w * m + 0.2 * (Z[b] == 1) * np.isin(np.arange(nA), [i, j])[None, :]
            add[:6] -= 0.3 * prev[:6]      # hosts change: no per-agent persistence beyond the shared prevalence
            return add
        E, _ = sim_elements(rng, P, Xag, n_el, hosts=hosts, extra=extra)
        truth["planted"]["memeplex"] = [int(nb + k) for k in range(6)]
        truth["planted"]["pair+memeplex"] = sorted(truth["planted"]["pair"] + truth["planted"]["memeplex"])
    Q = make_panel(P, Xag, A, R, E, [f"el{k}" for k in range(E.shape[0])], owner_override)
    truth["own"] = {}
    for r in art:
        if own_row[r] >= 0:
            truth["own"].setdefault(int(own_row[r]), []).append(int(r))
    return Q, truth


def components(r: dict) -> list:
    """True coupling components of a synthetic world: each agent with the artifacts its state drives; in W_nested the
    two pair agents, the shared artifact and the planted memeplex form one component."""
    comp = [set([int(a)] + [int(x) for x in v]) for a, v in r["own"].items()]
    pl_ = r["planted"]
    if "pair" in pl_:
        big = set(pl_["pair"]) | set(pl_.get("memeplex", []))
        rest = []
        for c in comp:
            if c & big:
                big |= c
            else:
                rest.append(c)
        comp = rest + [big]
    return comp


def is_false(r: dict, atoms, agents_worth: int) -> bool:
    """A multi-agent (or multi-element) system that does not sit inside one true component."""
    if agents_worth < 2:
        return False
    return not any(set(atoms) <= c for c in components(r))


def evaluate(Q, truth, res, sing):
    D = [d["atoms"] for d in res["discovered"]]
    out = {"n_disc": len(D), "n_exact": res["n_exact"]}
    planted = list(truth["planted"].values())
    multi = [X for X in D if L.agents_worth(Q, X) >= 2 or sum(Q.kind[a] == "element" for a in X) >= 2
             or any(Q.kind[a] == "room" for a in X)]
    out["n_multi"] = len(multi)
    r_ = {"own": truth["own"], "planted": truth["planted"]}
    out["n_false_multi"] = sum(is_false(r_, X, max(L.agents_worth(Q, X), 2 if sum(Q.kind[a] == "element" for a in X)
                                                   >= 2 or any(Q.kind[a] == "room" for a in X) else 0))
                               for X in multi)
    for k, T in truth["planted"].items():
        out[f"rec_{k}"] = bool(any(L.jacc(X, T) >= 0.5 for X in D))
        out[f"best_j_{k}"] = round(max([L.jacc(X, T) for X in D], default=0.0), 3)
    # P1: agent atoms individual (single-atom test on both halves)
    si = {r["atom"]: r["individual"] for r in sing}
    out["agent_single_share"] = float(np.mean([si[int(a)] for a in Q.agent_rows]))
    pd = {int(a): np.unique(Q.day[Q.present[i]]).size for i, a in enumerate(Q.agent_rows)}
    ag10 = [int(a) for a in Q.agent_rows if pd[int(a)] >= 10]
    in_own = {int(a) for a in ag10 for X in D if int(a) in X and L.agents_worth(Q, X) == 1 and len(X) >= 2}
    out["p1_share"] = float(np.mean([si[a] or a in in_own for a in ag10]))
    # P2: agents with an own artifact whose smallest discovered system containing them is agent + own artifact
    n_own, n_p2 = 0, 0
    for a in Q.agent_rows:
        own = truth["own"].get(int(a), [])
        if not own:
            continue
        n_own += 1
        cont = [X for X in D if int(a) in X]
        if cont:
            sm = min(cont, key=len)
            n_p2 += bool(set(sm) & set(own)) and L.agents_worth(Q, sm) == 1
    out["p2_share"] = n_p2 / max(n_own, 1)
    if "field_elements" in truth:
        fe = set(truth["field_elements"])
        out["n_field_disc"] = sum(bool(set(X) & fe) and sum(Q.kind[a] == "element" for a in X) >= 2 for X in D)
    if "pair" in truth["planted"]:
        pm = [X for X in D if L.jacc(X, truth["planted"]["pair"]) >= 0.5]
        mem = [X for X in D if any(a in X for a in truth["pair_agents"]) and L.agents_worth(Q, X) == 1]
        out["nest_pair_over_member"] = bool(any(set(y) < set(x) for x in pm for y in mem))
        if "memeplex" in truth["planted"]:
            mm = [X for X in D if L.jacc(X, truth["planted"]["memeplex"]) >= 0.5]
            out["nest_contains_both"] = bool(any(set(p) <= set(X) and set(m) <= set(X) for X in D
                                                 for p in pm for m in mm))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--rep0", type=int, default=0)
    ap.add_argument("--worlds", default="W_atoms,W_field,W_nested")
    ap.add_argument("--width", type=int, default=30)
    ap.add_argument("--rho", type=float, default=0.7)
    ap.add_argument("--w", type=float, default=0.4)
    ap.add_argument("--n-el", type=int, default=N_EL)
    ap.add_argument("--z-add", type=float, default=L.Z_ADD)
    ap.add_argument("--z-keep", type=float, default=L.Z_KEEP)
    ap.add_argument("--shuffle", action="store_true", help="rotate every atom within day (P7 calibrator)")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()
    SYN.mkdir(parents=True, exist_ok=True)
    kw = dict(z_add=args.z_add, z_keep=args.z_keep)
    if args.profile:
        Q, truth = world("W_nested", 0, args.width, args.rho, args.w, args.n_el)
        ev = L.Evaluator(Q)
        cp = L.Coupler(ev, 0)
        cands = [a for a in range(Q.nA) if a != 1]
        t0 = time.time()
        cp.increments((1,), cands, 0)
        dt1 = time.time() - t0
        print(f"atoms {Q.nA}; one step ({len(cands)} candidates x {L.R_STEP + 1} rows): {dt1:.2f} s "
              f"({1e3 * dt1 / len(cands):.1f} ms per candidate)")
        t0 = time.time()
        s = L.Search(cp, 0, seeds=[truth["planted"]["pair"][0]], **kw)
        r = s.run()
        print(f"one seed: {time.time() - t0:.2f} s, expanded {s.n_expanded}, terminals {r['terminals']}")
        t0 = time.time()
        sg = L.singles(ev, list(Q.agent_rows[:4]))
        print(f"4 single-atom tests (both halves): {time.time() - t0:.2f} s", [round(x['p_h0'], 3) for x in sg])
        return
    path = SYN / f"synthetic_w{args.width}_el{args.n_el}{args.tag}.jsonl"
    done = set()
    if path.exists():
        for ln in path.read_text().splitlines():
            r = json.loads(ln)
            done.add((r["world"], r["rep"]))
    for wname in args.worlds.split(","):
        for rep in range(args.rep0, args.rep0 + args.reps):
            if (wname, rep) in done:
                continue
            t0 = time.time()
            Q, truth = world(wname, rep, args.width, args.rho, args.w, args.n_el)
            if args.shuffle:
                rng = np.random.default_rng(77 + rep)
                Q = Q.with_S(IND.rotate_within_day(Q.S, Q.day, rng))
            res = L.discover(Q, seed=rep, **kw)
            sing = L.singles(res["ev"], list(Q.agent_rows), seed=rep)
            ev = evaluate(Q, truth, res, sing)
            row = {"world": wname, "rep": rep, "width": args.width, "rho": args.rho, "w": args.w,
                   "n_el": args.n_el, "shuffle": args.shuffle, **kw, **ev,
                   "n_maxima_h0": len(res["per_half"][0]["maxima"]), "n_maxima_h1": len(res["per_half"][1]["maxima"]),
                   "n_hold_h0": sum(m["holds"] for m in res["per_half"][0]["maxima"]),
                   "n_hold_h1": sum(m["holds"] for m in res["per_half"][1]["maxima"]),
                   "discovered": [d["atoms"] for d in res["discovered"]], "planted": truth["planted"],
                   "maxima": {h: [{"atoms": m["atoms"], "z_oos": round(m["z_oos"], 3),
                                   "min_oos": round(float(min(m["cohesion_oos"])), 3), "holds": m["holds"],
                                   "agents_worth": L.agents_worth(Q, m["atoms"])}
                                  for m in res["per_half"][h]["maxima"]] for h in (0, 1)},
                   "own": truth["own"],
                   "secs": round(time.time() - t0, 1), "n_evals": res["n_evals"]}
            with open(path, "a") as f:
                f.write(json.dumps(row) + "\n")
            print(wname, rep, {k: row[k] for k in row if k not in ("discovered", "planted", "maxima", "own")}, flush=True)


if __name__ == "__main__":
    main()
