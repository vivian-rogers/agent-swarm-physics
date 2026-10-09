"""H148 library: batched held-out Krakauer scores for many candidate systems, single-atom individuality tests,
day-permutation coupling nulls, the beam search (Krakauer boundary expansion with a beam), local maxima,
out-of-sample scoring, the two-direction agreement rule, matched random systems (card's null, reported) and nesting.

Estimator (card "Model"; Round 1 amendments A1-A4 in the card):
  system X = a set of atoms; its state = the tuple of its atoms' states, mixed-radix encoded, coarse-grained to 8
  symbols by the system's own leading composition on the codebook half (top 7 tuples -> 0..6, the rest -> 7).
  Environment E at the source bin (lagged): phase (3: first / middle / last bin of the day) x exogenous input (3: none /
  automated operator only / human or relayed human input) x rest-of-village presence above / below its day mean (2;
  the rest excludes the system's own agents, so E' = the environment without the system) = 18 cells.
  Held-out log-losses (bits per transition), leave-one-day-out by total-minus-day count tables; the smoothing is
  exactly `infra/shared/individuality.py: krakauer_discrete` (Dirichlet alpha = 0.5 tables for p0, p(x'|x), p(x'|e);
  p(x'|x,e) backs off to p(x'|x) with weight beta = 2), batched over systems with np.bincount on integer-encoded
  joints. A* = L0 - Lx (organismal), A = Le - Lxe (colonial), nC = Lx - Lxe. `verify()` checks the batch against
  krakauer_discrete.
Scores (A1):
  single atoms: an atom is an individual on a half when its colonial A beats within-(day, E) permutations of its
    source states (Besag-Clifford, h = 10, <= 300 draws; p <= 0.025, about z >= 2); it must hold on both halves.
  coupling z_g(a | X): A(X + a) against A(X + a with a's days permuted) (day-permutation null: a derangement of a's
    days within blocks of 6 same-parity days; keeps a's within-day dynamics, its phase alignment and its alphabet
    use; breaks its same-day alignment with X). 20 draws per candidate in the search.
  integration z_int(X): A(X) against A with every member's days permuted independently (sequential, <= 300 draws).
Search: from every atom, add atoms with z_g >= Z_ADD (3.0); beam 3; cap 10. Local maximum: a terminal of >= 2 atoms
whose every member couples to the rest (z_g(b | X - b) >= 2). Holds out of sample: z_int >= 2 on the other half (the
search half's codebook) and every member's z_g >= 1 there. Discovered: a held local maximum of one direction matched
by one of the other direction (A2: Jaccard >= 0.5; exact matches also counted).
The card's matched random systems (NullBank: same kinds, matched in the kind's single-atom A tercile) give a
secondary excess z for every discovered individual.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import individuality as IND  # noqa: E402

OUT = ROOT / "data/processed/H148-agent-discovery-51"
ALPHA, BETA = IND.ALPHA, IND.BETA
KX, KE = 8, 18
N0_DRAWS, N_MAX_DRAWS, H_STOP = 40, 300, 10
BEAM, CAP = 3, 10
ZMIN = 2.0            # mean member coupling z on the other half
N_OOS = 60            # day-permutation draws per member for the other-half test
Z_ADD = 3.0           # coupling z_tau needed to add an atom (selection over all candidates, so stricter than 2)
Z_KEEP = 2.0          # every member's coupling to the rest, search half
Z_OOS_KEEP = 1.0      # every member's coupling to the rest, other half
AGREE = 0.5           # Jaccard agreement of the two directions
R_STEP = 40           # day-permutation draws per candidate in a search step (final z)
R_STAGE1 = 8          # first-stage draws for every candidate; the rest only for candidates with z >= SCREEN
SCREEN = 1.0
BLOCK = 6             # day-permutation blocks: 6 same-parity days
CBATCH = 1400         # rows per coupling batch
SD_FLOOR = 0.002      # bits; floor on the null sd of tau (sparse atoms give near-constant nulls)
STAT = "heldout"      # coupling statistic: held-out log-loss transfer terms, or "plugin" CMI
E_MODE = "full"       # environment in the coupling terms: full E (18 cells), "exo" (6) or "none"
MIN_TRANS = 40        # a row needs >= 40 valid transitions on the half
MIN_NZ = 20           # an atom enters a half's search only with >= 20 bins outside its modal state (agents: present
                      # bins) and >= 4 span days there
P_SINGLE = 0.025
TOL_NC = 0.02
BATCH = 192


# ============================================================================== panel
@dataclass
class Panel:
    S: np.ndarray            # (n_atoms, nB) int8 states
    K: np.ndarray            # alphabet per atom
    kind: np.ndarray         # 'agent' | 'artifact' | 'room' | 'element'
    names: list
    agent_of: np.ndarray     # agent id for agent atoms, -1 otherwise
    owner: np.ndarray        # owner agent id (artifacts), agent id for agents, -1 otherwise
    day: np.ndarray          # day index per bin (0..nD-1)
    valid: np.ndarray        # bool per bin
    phase: np.ndarray        # 0/1/2 per bin
    exo: np.ndarray          # 0 none / 1 automated only / 2 human or relayed
    width: int = 30
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        self.S = np.asarray(self.S, np.int8)
        self.K = np.asarray(self.K, np.int64)
        self.nA, self.nB = self.S.shape
        self.is_agent = self.kind == "agent"
        self.agent_rows = np.flatnonzero(self.is_agent)
        self.present = (self.S[self.agent_rows] > 0)
        self.n_present = self.present.sum(0).astype(np.int16)
        self.b0 = IND.transitions(self.day, self.valid)
        self.tday = self.day[self.b0 + 1]
        self.radix = self.K.astype(np.int64)

    def half_trans(self, h: int) -> np.ndarray:
        """Transitions whose target day index has parity h (h = 0: active days 1, 3, 5, ... = 'odd days')."""
        return np.flatnonzero((self.tday % 2) == h)

    def half_bins(self, h: int) -> np.ndarray:
        return np.flatnonzero(self.valid & ((self.day % 2) == h))

    def with_S(self, S2: np.ndarray) -> "Panel":
        return Panel(S2, self.K, self.kind, self.names, self.agent_of, self.owner, self.day, self.valid, self.phase,
                     self.exo, self.width, dict(self.meta))


def load_panel(width: int = 30, with_elements: bool = True) -> Panel:
    z = np.load(OUT / f"atoms_{width}.npz")
    at = pl.read_parquet(OUT / "atoms.parquet")
    bins = pl.read_parquet(OUT / f"bins_{width}.parquet")
    S, K = z["S"], z["K"].astype(np.int64)
    kind = at["kind"].to_numpy().astype(object)
    names = at["name"].to_list()
    agent_of = at["agent"].to_numpy().astype(np.int64)
    owner = at["owner"].to_numpy().astype(np.int64)
    meta = {"atom_table": at, "resets": z["resets"], "agents": z["agents"]}
    ef = OUT / f"elements_{width}.npz"
    if with_elements and ef.exists():
        e = np.load(ef, allow_pickle=True)
        S = np.vstack([S, e["S"]])
        K = np.r_[K, e["K"]]
        kind = np.r_[kind, np.array(["element"] * e["S"].shape[0], object)]
        names = names + list(e["names"])
        agent_of = np.r_[agent_of, -np.ones(e["S"].shape[0], np.int64)]
        owner = np.r_[owner, -np.ones(e["S"].shape[0], np.int64)]
        meta["element_meta"] = json.loads(str(e["meta"]))
    exo = np.where(bins["exog_h"].to_numpy() > 0, 2, (bins["exog"].to_numpy() > 0).astype(np.int8)).astype(np.int8)
    return Panel(S, K, kind, names, agent_of, owner, bins["day"].to_numpy().astype(np.int64),
                 bins["valid"].to_numpy(), bins["phase"].to_numpy().astype(np.int64), exo, width, meta)


# ============================================================================== batched evaluator
def _heldout(idx: np.ndarray, rd: np.ndarray, n: int, nD: int, size: int) -> np.ndarray:
    """idx (rows x nt) cell index per transition, rd (rows x nt) = row * nD + day. Returns total-minus-own-day counts
    of each transition's cell, per row (one bincount for the day tables)."""
    rows = rd // nD
    dc = np.bincount((rd * size + idx).ravel(), minlength=n * nD * size).reshape(n, nD, size)
    tot = dc.sum(1)
    d = rd % nD
    return tot[rows, idx] - dc[rows, d, idx]


def batch_losses(x: np.ndarray, xp: np.ndarray, e: np.ndarray, dd: np.ndarray, nD: int,
                 w: np.ndarray | None = None) -> dict:
    """Held-out losses for n systems at once. x, xp, e: (n, nt) int64 (x, x' in 0..KX-1, e in 0..KE-1);
    dd: (nt,) day index 0..nD-1 shared by all rows; w: (n, nt) bool, the row's valid transitions (DQ8 trim: every
    agent atom of the system present at both bins). Invalid transitions go to a dummy row that is never read. Same
    smoothing as individuality.krakauer_discrete."""
    n0_, nt = x.shape
    w = np.ones((n0_, nt), bool) if w is None else np.asarray(w, bool)
    r = np.where(w, np.arange(n0_, dtype=np.int64)[:, None], n0_)
    n = n0_ + 1
    rd = r * nD + dd[None, :]
    Nd = np.bincount(rd.ravel(), minlength=n * nD).reshape(n, nD)
    n_all = Nd.sum(1)[r] - Nd[r, dd[None, :]]
    n0 = _heldout(xp, rd, n, nD, KX)
    p0 = (n0 + ALPHA) / (n_all + ALPHA * KX)
    nx = _heldout(x, rd, n, nD, KX)
    nxx = _heldout(x * KX + xp, rd, n, nD, KX * KX)
    px = (nxx + ALPHA) / (nx + ALPHA * KX)
    ne = _heldout(e, rd, n, nD, KE)
    nex = _heldout(e * KX + xp, rd, n, nD, KE * KX)
    pe = (nex + ALPHA) / (ne + ALPHA * KX)
    xe = x * KE + e
    nxe = _heldout(xe, rd, n, nD, KX * KE)
    nxex = _heldout(xe * KX + xp, rd, n, nD, KX * KE * KX)
    pxe = (nxex + BETA * px) / (nxe + BETA)
    nv = w.sum(1)
    m = lambda p: np.where(nv >= MIN_TRANS, (-np.log2(p) * w).sum(1) / np.maximum(nv, 1), np.nan)  # noqa: E731
    L0, Lx, Le, Lxe = m(p0), m(px), m(pe), m(pxe)
    return {"L0": L0, "Lx": Lx, "Le": Le, "Lxe": Lxe, "Astar": L0 - Lx, "A": Le - Lxe, "nC": Lx - Lxe, "n": nv}


class Evaluator:
    """Scores batches of systems with the codebook fitted on half hc and log-losses on half he."""

    def __init__(self, P: Panel):
        self.P = P
        self.cb_bins = {h: P.half_bins(h) for h in (0, 1)}
        self.tr = {h: P.half_trans(h) for h in (0, 1)}
        self.dd = {}
        for h in (0, 1):
            _, self.dd[h] = np.unique(P.tday[self.tr[h]], return_inverse=True)
        vb = np.flatnonzero(P.valid)
        self.vb = vb
        self.seg_start = np.r_[0, np.flatnonzero(np.diff(P.day[vb])) + 1]
        self.seg_day = P.day[vb][self.seg_start]
        self.base_e = (P.phase.astype(np.int64) * 3 + P.exo.astype(np.int64)) * 2
        self.agent_pos = -np.ones(P.nA, np.int64)
        self.agent_pos[P.agent_rows] = np.arange(P.agent_rows.size)
        self.n_evals = 0

    def pres_mask(self, systems: list) -> np.ndarray:
        """(n, nB) bool: every agent atom of the system present in the bin (DQ8 trim, A6)."""
        P = self.P
        M = np.ones((len(systems), P.nB), bool)
        for r, X in enumerate(systems):
            for a in X:
                if self.agent_pos[a] >= 0:
                    M[r] &= P.present[self.agent_pos[a]]
        return M

    def codes(self, systems: list) -> np.ndarray:
        P = self.P
        C = np.zeros((len(systems), P.nB), np.int64)
        for r, X in enumerate(systems):
            for a in X:
                C[r] = C[r] * P.radix[a] + P.S[a]
        return C

    def coarse(self, C: np.ndarray, hc: int, M: np.ndarray | None = None) -> np.ndarray:
        """Top-7 tuples on the codebook half (bins where M is true) -> 0..6 (ties by code), the rest -> 7."""
        n = C.shape[0]
        cb = self.cb_bins[hc]
        big = int(C.max()) + 1
        rows = np.repeat(np.arange(n, dtype=np.int64), cb.size)
        key = rows * big + C[:, cb].ravel()
        if M is not None:
            key = key[M[:, cb].ravel()]
        u, cnt = np.unique(key, return_counts=True)
        if u.size == 0:
            return np.full(C.shape, KX - 1, np.int64)
        ur = u // big
        order = np.lexsort((u, -cnt, ur))
        first = np.r_[0, np.flatnonzero(np.diff(ur[order])) + 1]
        rank = np.empty(u.size, np.int64)
        rr = np.repeat(first, np.diff(np.r_[first, u.size]))
        rank[order] = np.arange(u.size) - rr
        symu = np.minimum(rank, KX - 1)
        allkey = np.arange(n, dtype=np.int64)[:, None] * big + C
        ix = np.minimum(np.searchsorted(u, allkey), u.size - 1)
        found = u[ix] == allkey
        return np.where(found, symu[ix], KX - 1).astype(np.int64)

    def env(self, systems: list) -> np.ndarray:
        P = self.P
        M = np.zeros((len(systems), P.nA), np.float64)
        for r, X in enumerate(systems):
            M[r, list(X)] = 1.0
        M = M[:, P.agent_rows]
        rest = P.n_present[None, :].astype(np.float64) - M @ P.present.astype(np.float64)
        rt = rest[:, self.vb]
        sums = np.add.reduceat(rt, self.seg_start, axis=1)
        lens = np.diff(np.r_[self.seg_start, self.vb.size])
        mean_day = np.zeros((len(systems), P.day.max() + 1))
        mean_day[:, self.seg_day] = sums / lens
        high = (rest > mean_day[:, P.day]).astype(np.int64)
        return self.base_e[None, :] + high

    def env_cached(self, systems: list) -> np.ndarray:
        """env() for a list with repeats: one row per distinct system, cached (E' depends only on the agent set)."""
        if not hasattr(self, "_env_cache"):
            self._env_cache = {}
        P = self.P
        keys = [tuple(a for a in X if P.is_agent[a]) for X in systems]
        todo = [k for k in dict.fromkeys(keys) if k not in self._env_cache]
        if todo:
            rows = self.env(todo)
            for k, r in zip(todo, rows):
                self._env_cache[k] = r
        return np.stack([self._env_cache[k] for k in keys])

    def losses(self, sym: np.ndarray, E: np.ndarray, he: int, M: np.ndarray | None = None) -> dict:
        t = self.tr[he]
        b0 = self.P.b0[t]
        dd = self.dd[he]
        self.n_evals += sym.shape[0]
        w = None if M is None else (M[:, b0] & M[:, b0 + 1])
        return batch_losses(sym[:, b0], sym[:, b0 + 1], E[:, b0], dd, int(dd.max()) + 1, w)

    def score(self, systems: list, hc: int, hes=(None,)) -> dict:
        """Scores on half hc (codebook and loss) and, for each he in hes, on half he with the hc codebook."""
        out = {}
        for i in range(0, len(systems), BATCH):
            ch = systems[i:i + BATCH]
            M = self.pres_mask(ch)
            sym = self.coarse(self.codes(ch), hc, M)
            E = self.env(ch)
            for h in (hc,) + tuple(x for x in hes if x is not None and x != hc):
                v = self.losses(sym, E, h, M)
                o = out.setdefault(h, {k: [] for k in v})
                for k in o:
                    o[k].append(v[k])
        return {h: {k: np.concatenate(v) for k, v in o.items()} for h, o in out.items()}

    # --- single-atom individuality (A1)
    def single_test(self, a: int, he: int, rng: np.random.Generator, n_max: int = N_MAX_DRAWS) -> dict:
        """Colonial A of atom a on half he vs within-(day, E) permutations of its source states (Besag-Clifford)."""
        P = self.P
        t = self.tr[he]
        b0 = P.b0[t]
        dd = self.dd[he]
        nD = int(dd.max()) + 1
        M = self.pres_mask([(a,)])[0]
        keep = M[b0] & M[b0 + 1]
        b0, dd = b0[keep], dd[keep]
        sym = self.coarse(self.codes([(a,)]), he, M[None])[0]
        e = self.env([(a,)])[0][b0]
        x, xp = sym[b0], sym[b0 + 1]
        if b0.size < MIN_TRANS:
            return {"A": np.nan, "p": 1.0, "z": np.nan, "draws": 0, "nC": np.nan, "Astar": np.nan}
        obs = batch_losses(x[None], xp[None], e[None], dd, nD)
        A = float(obs["A"][0])
        strat = dd * KE + e
        so = np.argsort(strat, kind="stable")
        ss = strat[so]
        draws = []
        k = 0
        while len(draws) < n_max:
            m = min(50, n_max - len(draws))
            key = rng.random((m, so.size))
            # within-stratum shuffle: sort by (stratum, random) per row
            order = np.argsort(ss[None, :] * 2.0 + key, axis=1, kind="stable")   # ss integer, key in [0,1)
            xs = np.empty((m, so.size), np.int64)
            xs[:, so] = x[so][order]
            v = batch_losses(xs, np.broadcast_to(xp, (m, xp.size)), np.broadcast_to(e, (m, e.size)), dd, nD)["A"]
            self.n_evals += m
            for val in v:
                draws.append(float(val))
                k += val >= A
                if k >= H_STOP:
                    break
            if k >= H_STOP:
                break
        d = np.asarray(draws)
        n = d.size
        p = k / n if (k >= H_STOP and n < n_max) else (k + 1) / (n + 1)
        sd = d.std(ddof=1) if n > 1 else np.nan
        return {"A": A, "p": float(p), "z": float((A - d.mean()) / sd) if sd > 0 else np.nan, "draws": int(n),
                "nC": float(obs["nC"][0]), "Astar": float(obs["Astar"][0])}


# ============================================================================== null banks
class NullBank:
    """Matched random systems per (signature, codebook half): A, nC, A* on both halves (A3: atoms matched on kind
    and the kind's tercile of single-atom A on the codebook half)."""

    def __init__(self, ev: Evaluator, seed: int = 0, band_by: str = "A"):
        self.ev = ev
        P = ev.P
        self.rng = np.random.default_rng(seed)
        singles = [(a,) for a in range(P.nA)]
        self.band = {}
        for hc in (0, 1):
            if band_by == "A":
                v = ev.score(singles, hc)[hc]["A"]
            else:   # activity (card's literal matching)
                v = (P.S > 0)[:, P.half_bins(hc)].sum(1).astype(float)
            band = np.zeros(P.nA, np.int8)
            for k in np.unique(P.kind):
                ix = np.flatnonzero(P.kind == k)
                if ix.size < 6:
                    continue
                q = np.quantile(v[ix], [1 / 3, 2 / 3])
                band[ix] = (v[ix] > q[0]).astype(np.int8) + (v[ix] > q[1]).astype(np.int8)
            self.band[hc] = band
        self.pools = {}
        for hc in (0, 1):
            for k in np.unique(P.kind):
                for b in range(3):
                    ix = np.flatnonzero((P.kind == k) & (self.band[hc] == b))
                    if ix.size:
                        self.pools[(hc, k, b)] = ix
        self.bank = {}

    def signature(self, X, hc: int) -> tuple:
        P = self.ev.P
        return tuple(sorted((P.kind[a], int(self.band[hc][a])) for a in X))

    def _draw(self, sig: tuple, hc: int, m: int) -> list:
        need = {}
        for s in sig:
            need[s] = need.get(s, 0) + 1
        out = []
        for _ in range(m):
            X = []
            for s, c in need.items():
                pool = self.pools[(hc,) + s]
                X.extend(self.rng.choice(pool, size=min(c, pool.size), replace=False).tolist())
            out.append(tuple(sorted(X)))
        return out

    def get(self, sig: tuple, hc: int, m: int = N0_DRAWS) -> dict:
        key = (sig, hc)
        cur = self.bank.get(key)
        have = 0 if cur is None else cur["A"][hc].size
        if have < m:
            sc = self.ev.score(self._draw(sig, hc, m - have), hc, hes=(1 - hc,))
            new = {q: {h: sc[h][q] for h in sc} for q in ("A", "nC", "Astar")}
            if cur is None:
                cur = new
            else:
                for q in new:
                    for h in new[q]:
                        cur[q][h] = np.r_[cur[q][h], new[q][h]]
            self.bank[key] = cur
        return cur

    def z(self, sig: tuple, hc: int, A, he: int | None = None) -> np.ndarray:
        b = self.get(sig, hc)
        a = b["A"][hc if he is None else he][:N0_DRAWS]
        sd = a.std(ddof=1) if a.size > 1 else np.nan
        return (np.asarray(A) - a.mean()) / max(sd, 1e-9)

    def sequential(self, sig: tuple, hc: int, A: float, he: int | None = None) -> dict:
        """Extend the bank toward N_MAX_DRAWS; Besag-Clifford stop at H_STOP exceedances."""
        h = hc if he is None else he
        m = N0_DRAWS
        while True:
            a = self.get(sig, hc, m)["A"][h][:m]
            exc = int((a >= A).sum())
            if exc >= H_STOP or m >= N_MAX_DRAWS:
                break
            m = min(N_MAX_DRAWS, m + 65)
        p = exc / m if exc >= H_STOP else (exc + 1) / (m + 1)
        sd = a.std(ddof=1)
        return {"z": float((A - a.mean()) / max(sd, 1e-9)), "p": float(p), "draws": int(m), "exceed": exc,
                "null_mean": float(a.mean()), "null_sd": float(sd)}


# ============================================================================== day-permutation nulls (A1)
class DayPerms:
    """Per-atom day-permutation nulls (A1). For atom a, its eligible days are those from its first to its last day
    with a nonzero state (agents: present days; artifacts and elements: from first to last activity). Blocks of
    BLOCK consecutive same-parity eligible days; each draw is a derangement within every block. A draw maps bin
    (day d, slot k) to (day pi(d), slot k): it keeps the atom's within-day dynamics and phase alignment and breaks its
    same-day alignment with every other atom. Days outside the span map to themselves (the atom is 0 there)."""

    def __init__(self, P: Panel, rng: np.random.Generator, n: int = N_MAX_DRAWS, block: int = BLOCK):
        self.P, self.rng, self.n, self.block = P, rng, n, block
        nD = int(P.day.max()) + 1
        self.nD = nD
        first = np.full(nD, -1, np.int64)
        for b in range(P.nB - 1, -1, -1):
            first[P.day[b]] = b
        self.first = first
        self.slot = np.arange(P.nB) - first[P.day]
        self.nper = np.bincount(P.day, minlength=nD)
        nz = (P.S > 0)
        # variation per half: bins outside the atom's modal state (agents: among present bins only)
        isag = P.kind == "agent"
        self.nz_half = np.zeros((P.nA, 2), np.int64)
        for h in (0, 1):
            hb = P.valid & ((P.day % 2) == h)
            for a in range(P.nA):
                v = P.S[a][hb & (nz[a] if isag[a] else True)]
                if v.size:
                    self.nz_half[a, h] = v.size - np.bincount(v).max()
        dayany = np.zeros((P.nA, nD), bool)
        np.logical_or.at(dayany.T, P.day, nz.T)
        self.span = []
        for a in range(P.nA):
            d = np.flatnonzero(dayany[a])
            self.span.append((int(d[0]), int(d[-1])) if d.size else (0, -1))
        self.cache = {}

    def eligible(self, a: int, h: int) -> bool:
        lo, hi = self.span[a]
        nd = sum(1 for d in range(lo, hi + 1) if d % 2 == h)
        return bool(self.nz_half[a, h] >= MIN_NZ and nd >= 4)

    def _blocks(self, a: int) -> list:
        lo, hi = self.span[a]
        out = []
        for h in (0, 1):
            dh = np.array([d for d in range(lo, hi + 1) if d % 2 == h], np.int64)
            bl = [dh[i:i + self.block] for i in range(0, dh.size, self.block)]
            if len(bl) >= 2 and bl[-1].size == 1:
                bl[-2] = np.r_[bl[-2], bl[-1]]
                bl = bl[:-1]
            out.extend(b for b in bl if b.size >= 2)
        return out

    def day_maps(self, a: int) -> np.ndarray:
        """(n, nD) day permutations for atom a (cached)."""
        if a not in self.cache:
            M = np.tile(np.arange(self.nD, dtype=np.int64), (self.n, 1))
            for blk in self._blocks(a):
                k = blk.size
                for r in range(self.n):
                    while True:
                        pi = self.rng.permutation(k)
                        if not (pi == np.arange(k)).any():
                            break
                    M[r, blk] = blk[pi]
            self.cache[a] = M
        return self.cache[a]

    def series(self, a: int, idx: np.ndarray) -> np.ndarray:
        """Atom a's state series under draws idx: (len(idx), nB)."""
        M = self.day_maps(a)[idx]                               # (m, nD)
        P = self.P
        tgt_day = M[:, P.day]                                   # (m, nB)
        b = self.first[tgt_day] + np.minimum(self.slot[None, :], self.nper[tgt_day] - 1)
        return P.S[a][b]


KA = 5   # largest single-atom alphabet (agent atoms); used for encoding only


def _heldout_sparse(row: np.ndarray, day: np.ndarray, cell: np.ndarray, nD: int) -> np.ndarray:  # noqa: D401
    """Per transition: count of its (row, cell) over all days minus its own day's count (sort-based; any cell size)."""
    big = int(cell.max()) + 1
    k1 = row * big + cell
    _, inv1, c1 = np.unique(k1, return_inverse=True, return_counts=True)
    k2 = (row * nD + day) * big + cell
    _, inv2, c2 = np.unique(k2, return_inverse=True, return_counts=True)
    return (c1[inv1] - c2[inv2]).astype(np.float64)


def _dir(row, day, nD, ctx, tgt, K, back=None):
    """Held-out p(tgt | ctx): Dirichlet(ALPHA) table, or interpolated back-off to `back` with weight BETA."""
    nc = _heldout_sparse(row, day, ctx * KMAX + tgt, nD)
    nx = _heldout_sparse(row, day, ctx, nD)
    if back is None:
        return (nc + ALPHA) / (nx + ALPHA * K)
    return (nc + BETA * back) / (nx + BETA)


KMAX = 8


def cross_info(x, xp, a, ap, e, dd, nD, Ka, w=None) -> dict:
    """Held-out transfer terms for n rows at once (bits per transition).
    x, xp: (n, nt) system state and next state (0..KX-1); a, ap: (n, nt) candidate atom state and next (0..Ka-1);
    e: (n, nt) environment (0..KE-1); dd: (nt,) day index; Ka: (n,) alphabet of the candidate.
    T_aX = L(x'|x,E) - L(x'|x,a,E) = I(x'; a | x, E): what a, left in the environment, tells about the system's future
    (the part of the system's nC that a carries). T_Xa = L(a'|a,E) - L(a'|a,x,E). tau = T_aX + T_Xa.
    Back-off chains: (x,e) -> x; (x,a,e) -> (x,a) -> x; same for a'."""
    n, nt = x.shape
    w = np.ones((n, nt), bool) if w is None else np.asarray(w, bool)
    row = np.where(w, np.arange(n, dtype=np.int64)[:, None], n).ravel()   # invalid transitions -> dummy row
    day = np.tile(np.asarray(dd, np.int64), n)
    x, xp, a, ap, e = (np.asarray(v, np.int64).ravel() for v in (x, xp, a, ap, e))
    K = np.repeat(np.asarray(Ka, np.float64), nt)
    px = _dir(row, day, nD, x, xp, KX)
    pxe = _dir(row, day, nD, x * KE + e, xp, KX, px)
    pxa = _dir(row, day, nD, x * KA + a, xp, KX, px)
    pxae = _dir(row, day, nD, (x * KA + a) * KE + e, xp, KX, pxa)
    pa = _dir(row, day, nD, a, ap, K)
    pae = _dir(row, day, nD, a * KE + e, ap, K, pa)
    pax = _dir(row, day, nD, a * KX + x, ap, K, pa)
    paxe = _dir(row, day, nD, (a * KX + x) * KE + e, ap, K, pax)
    nv = w.sum(1)
    m = lambda p: np.where(nv >= MIN_TRANS, ((-np.log2(p)).reshape(n, nt) * w).sum(1) / np.maximum(nv, 1),  # noqa: E731
                           np.nan)
    T_aX = m(pxe) - m(pxae)
    T_Xa = m(pae) - m(paxe)
    return {"T_aX": T_aX, "T_Xa": T_Xa, "tau": T_aX + T_Xa}


def _ent_rows(row: np.ndarray, cell: np.ndarray, n: int, nt: int) -> np.ndarray:
    """Plug-in entropy (bits) of `cell` within each row (rows of equal length nt)."""
    big = int(cell.max()) + 1
    u, c = np.unique(row * big + cell, return_counts=True)
    r = u // big
    p = c / nt
    return np.bincount(r, weights=-p * np.log2(p), minlength=n)


def cross_info_plugin(x, xp, a, ap, e, Ka) -> dict:
    """Plug-in transfer terms per row (bits): T_aX = I(x'; a | x, E), T_Xa = I(a'; x | a, E). Biased upward with
    many cells; the day-permutation null carries the same bias, so z is unbiased in that sense (A5)."""
    n, nt = x.shape
    row = np.repeat(np.arange(n, dtype=np.int64), nt)
    x, xp, a, ap, e = (np.asarray(v, np.int64).ravel() for v in (x, xp, a, ap, e))
    H = lambda c: _ent_rows(row, c, n, nt)   # noqa: E731
    cx = x * KE + e
    T_aX = H(cx * KX + xp) + H(cx * KA + a) - H(cx) - H((cx * KA + a) * KX + xp)
    ca = a * KE + e
    T_Xa = H(ca * KA + ap) + H(ca * KX + x) - H(ca) - H((ca * KX + x) * KA + ap)
    return {"T_aX": T_aX, "T_Xa": T_Xa, "tau": T_aX + T_Xa}


class Coupler:
    """Coupling tau(a, X) = T(a -> X) + T(X -> a) (Krakauer's nC drop when a moves from the environment into the
    system, both ways) against day-permutation nulls of a; all candidate additions of one step from one batch."""

    def __init__(self, ev: Evaluator, seed: int = 0, r_step: int = R_STEP, e_mode: str = E_MODE,
                 stat: str = STAT):
        self.ev = ev
        self.stat = stat
        self.rng = np.random.default_rng(seed)
        self.r_step = r_step
        self.e_mode = e_mode
        self.dp = DayPerms(ev.P, self.rng)

    def _e(self, E: np.ndarray) -> np.ndarray:
        if self.e_mode == "full":
            return E
        if self.e_mode == "exo":           # exogenous input x rest-of-village (phase is kept by the null)
            return E % 6
        return np.zeros_like(E)

    def _taus(self, X: tuple, xs: np.ndarray, MX: np.ndarray, cands: list, hs: tuple, nnull: int) -> dict:
        """Real tau and nnull day-permuted tau per candidate, per half: {h: (real (m,), null (m, nnull), T_aX, T_Xa)}."""
        P, ev = self.ev.P, self.ev
        per = nnull + 1
        step = max(1, CBATCH // per)
        res = {h: ([], [], [], []) for h in hs}
        for i in range(0, len(cands), step):
            ch = cands[i:i + step]
            Arows, envsys, Ka = [], [], []
            for a in ch:
                idx = self.rng.choice(self.dp.n, size=nnull, replace=False)
                Arows.append(P.S[a][None, :])
                Arows.append(self.dp.series(a, idx))
                envsys.extend([tuple(sorted(X + (a,)))] * per)
                Ka.extend([int(P.K[a])] * per)
            Am = np.vstack(Arows).astype(np.int64)
            # trim on the system's agents only: the candidate's absence is its state 0, so the real row and its
            # null rows use the same transitions (no sample-size bias in the held-out terms)
            E = self._e(ev.env_cached(envsys))
            for h in hs:
                b0 = P.b0[ev.tr[h]]
                dd = ev.dd[h]
                n = Am.shape[0]
                xb, xpb = np.broadcast_to(xs[b0], (n, b0.size)), np.broadcast_to(xs[b0 + 1], (n, b0.size))
                if self.stat == "plugin":
                    r = cross_info_plugin(xb, xpb, Am[:, b0], Am[:, b0 + 1], E[:, b0], Ka)
                else:
                    w = np.broadcast_to((MX[b0] & MX[b0 + 1])[None, :], (n, b0.size))
                    r = cross_info(xb, xpb, Am[:, b0], Am[:, b0 + 1], E[:, b0], dd, int(dd.max()) + 1, Ka, w)
                ev.n_evals += n
                tau = r["tau"].reshape(len(ch), per)
                res[h][0].append(tau[:, 0])
                res[h][1].append(tau[:, 1:])
                res[h][2].append(r["T_aX"].reshape(len(ch), per)[:, 0])
                res[h][3].append(r["T_Xa"].reshape(len(ch), per)[:, 0])
        return {h: tuple(np.concatenate(v) if v else np.zeros((0,)) for v in res[h]) for h in hs}

    @staticmethod
    def _z(real, null):
        mu, sd = np.nanmean(null, 1), np.nanstd(null, 1, ddof=1)
        return (real - mu) / np.maximum(sd, SD_FLOOR)

    def increments(self, X: tuple, cands: list, hc: int, hes=(), nnull: int | None = None) -> dict:
        """z_tau(a | X) for every a in cands on half hc (X's codebook from hc), and on each he in hes.
        Search mode (nnull None, hc only): two stages, R1 = 8 draws for every candidate, then 32 more for those with
        z >= SCREEN (final z from 40 draws, the calibrated setting). Otherwise nnull draws in one stage."""
        ev = self.ev
        hs = (hc,) + tuple(h for h in hes if h != hc)
        MX = ev.pres_mask([tuple(X)])[0]
        xs = ev.coarse(ev.codes([tuple(X)]), hc, MX[None])[0]
        out = {h: {k: np.zeros(len(cands)) for k in ("tau", "z", "T_aX", "T_Xa")} for h in hs}
        if not cands:
            return out
        two = nnull is None and len(hs) == 1
        r = self._taus(X, xs, MX, cands, hs, R_STAGE1 if two else nnull)
        for h in hs:
            real, null, tax, txa = r[h]
            z = self._z(real, null)
            if two:
                go = np.flatnonzero(np.nan_to_num(z, nan=-9) >= SCREEN)
                if go.size:
                    r2 = self._taus(X, xs, MX, [cands[k] for k in go], hs, R_STEP - R_STAGE1)[h]
                    z[go] = self._z(real[go], np.hstack([null[go], r2[1]]))
            out[h]["tau"], out[h]["z"], out[h]["T_aX"], out[h]["T_Xa"] = real, z, tax, txa
        return out


# ============================================================================== search
class Search:
    """Beam search from every single-atom seed on half hc (Krakauer's boundary rule with a beam, A1): add the atoms
    whose coupling to the system beats the day-permutation null (z_tau >= Z_ADD); keep the best `beam` children;
    stop when none qualifies or at the cap. A terminal of >= 2 atoms is a local maximum when every member couples to
    the rest (z_tau(b | X - b) >= Z_KEEP)."""

    def __init__(self, cp: Coupler, hc: int, cap: int = CAP, beam: int = BEAM, seeds: list | None = None,
                 z_add: float = Z_ADD, z_keep: float = Z_KEEP, atoms: list | None = None):
        self.cp, self.hc, self.cap, self.beam = cp, hc, cap, beam
        self.z_add, self.z_keep = z_add, z_keep
        base = range(cp.ev.P.nA) if atoms is None else atoms
        self.atoms = [a for a in base if cp.dp.eligible(a, hc)]
        self.seeds = list(self.atoms) if seeds is None else [a for a in seeds if a in self.atoms]
        self.children = {}
        self.n_expanded = 0

    def expand(self, X: tuple) -> dict:
        if X not in self.children:
            cands = [a for a in self.atoms if a not in X]
            inc = self.cp.increments(X, cands, self.hc)[self.hc]
            self.children[X] = {a: (float(inc["z"][j]), float(inc["tau"][j])) for j, a in enumerate(cands)}
            self.n_expanded += 1
        return self.children[X]

    def run(self, log_every: int = 0) -> dict:
        terminals = set()
        for si, s in enumerate(self.seeds):
            beam = [(s,)]
            seen = set()
            while beam:
                pool = {}
                for X in beam:
                    if X in seen:
                        continue
                    seen.add(X)
                    if len(X) >= self.cap:
                        terminals.add(X)
                        continue
                    adm = {a: v for a, v in self.expand(X).items() if v[0] >= self.z_add}
                    if not adm:
                        terminals.add(X)
                    for a, v in adm.items():
                        C = tuple(sorted(X + (a,)))
                        pool[C] = max(pool.get(C, -np.inf), v[0])
                beam = sorted(pool, key=lambda C: (-pool[C], C))[:self.beam]
            if log_every and (si + 1) % log_every == 0:
                print(f"  seed {si + 1}/{len(self.seeds)}: expanded {self.n_expanded}, terminals {len(terminals)},"
                      f" evals {self.cp.ev.n_evals}", flush=True)
        return {"terminals": sorted((X for X in terminals if len(X) >= 2), key=lambda X: (len(X), X))}

    def cohesion(self, X: tuple, h: int | None = None, nnull: int | None = None) -> list:
        """z_tau(b | X - b) for each member b, on half h (default: the search half), codebook from the search half."""
        h = self.hc if h is None else h
        out = []
        for b in X:
            rest = tuple(a for a in X if a != b)
            if h == self.hc and nnull is None and rest in self.children and b in self.children[rest]:
                out.append(self.children[rest][b][0])
                continue
            if not self.cp.dp.eligible(b, h):
                out.append(0.0)
                continue
            inc = self.cp.increments(rest, [b], self.hc, hes=(h,), nnull=nnull)
            out.append(float(inc[h]["z"][0]))
        return out

    def local_maxima(self, terminals) -> list:
        out = []
        for X in terminals:
            coh = self.cohesion(X)
            if min(coh) >= self.z_keep:
                out.append({"atoms": X, "cohesion": coh})
        return out


def out_of_sample(srch: Search, maxima: list) -> list:
    """Each local maximum of the hc search, scored on the other half with the hc codebook: every member's coupling
    to the rest (z_tau, 60 day-permutation draws). Holds: mean member z >= ZMIN and min member z >= Z_OOS_KEEP.
    Also the system's A, nC, A* on both halves (descriptors)."""
    hc = srch.hc
    he = 1 - hc
    if not maxima:
        return []
    sc = srch.cp.ev.score([tuple(m["atoms"]) for m in maxima], hc, hes=(he,))
    out = []
    for j, m in enumerate(maxima):
        coh = srch.cohesion(tuple(m["atoms"]), he, nnull=N_OOS)
        out.append({**m, "A": float(sc[hc]["A"][j]), "nC": float(sc[hc]["nC"][j]), "Astar": float(sc[hc]["Astar"][j]),
                    "A_oos": float(sc[he]["A"][j]), "nC_oos": float(sc[he]["nC"][j]),
                    "Astar_oos": float(sc[he]["Astar"][j]), "cohesion_oos": coh, "z_oos": float(np.mean(coh)),
                    "holds": bool(np.mean(coh) >= ZMIN and min(coh) >= Z_OOS_KEEP)})
    return out


def jacc(a, b) -> float:
    a, b = set(a), set(b)
    return len(a & b) / max(len(a | b), 1)


def singles(ev: Evaluator, atoms: list, seed: int = 0) -> list:
    """Single-atom individuality on both halves (A1)."""
    rng = np.random.default_rng(seed)
    out = []
    for a in atoms:
        r = {h: ev.single_test(a, h, rng) for h in (0, 1)}
        out.append({"atom": int(a), "A_h0": r[0]["A"], "A_h1": r[1]["A"], "p_h0": r[0]["p"], "p_h1": r[1]["p"],
                    "z_h0": r[0]["z"], "z_h1": r[1]["z"],
                    "individual": bool(r[0]["p"] <= P_SINGLE and r[1]["p"] <= P_SINGLE)})
    return out


def discover(P: Panel, seed: int = 0, cap: int = CAP, beam: int = BEAM, log_every: int = 0,
             seeds: list | None = None, z_add: float = Z_ADD, z_keep: float = Z_KEEP, agree: float = AGREE,
             atoms: list | None = None) -> dict:
    """Both directions; discovered individuals = local maxima that hold out of sample in one direction and are matched
    (Jaccard >= agree) by a held local maximum of the other direction (A2)."""
    ev = Evaluator(P)
    cp = Coupler(ev, seed)
    res = {}
    for hc in (0, 1):
        s = Search(cp, hc, cap, beam, seeds, z_add, z_keep, atoms)
        r = s.run(log_every)
        lm = s.local_maxima(r["terminals"])
        res[hc] = {"terminals": len(r["terminals"]), "expanded": s.n_expanded, "maxima": out_of_sample(s, lm)}
    held = {h: [m for m in res[h]["maxima"] if m["holds"]] for h in (0, 1)}
    disc = []
    for m0 in sorted(held[0], key=lambda m: -m["z_oos"]):
        best = max(((jacc(m0["atoms"], m1["atoms"]), j) for j, m1 in enumerate(held[1])), default=(0.0, -1))
        if best[0] >= agree:
            m1 = held[1][best[1]]
            core = sorted(set(m0["atoms"]) & set(m1["atoms"]))
            disc.append({"atoms": core if len(core) >= 2 else sorted(m0["atoms"]),
                         "atoms_h0": sorted(m0["atoms"]), "atoms_h1": sorted(m1["atoms"]), "jaccard": best[0],
                         "h0": strip(m0), "h1": strip(m1)})
    seen, D = set(), []
    for d in disc:
        k = tuple(d["atoms"])
        if k not in seen:
            seen.add(k)
            D.append(d)
    exact = len(set(tuple(m["atoms"]) for m in held[0]) & set(tuple(m["atoms"]) for m in held[1]))
    return {"discovered": D, "n_exact": exact,
            "per_half": {h: {"terminals": res[h]["terminals"], "expanded": res[h]["expanded"],
                             "maxima": [strip(m) for m in res[h]["maxima"]]} for h in (0, 1)},
            "n_evals": ev.n_evals, "ev": ev, "cp": cp}


def strip(m: dict) -> dict:
    return {k: (list(v) if isinstance(v, tuple) else v) for k, v in m.items() if k not in ("sig",)}


# ============================================================================== nesting and descriptors
def nesting(indiv: list) -> list:
    """Edges (i contains j) among individuals (atom-set inclusion); no exclusion postulate."""
    sets = [set(x["atoms"]) for x in indiv]
    return [(i, j) for i, a in enumerate(sets) for j, b in enumerate(sets) if i != j and b < a]


def scale_of(P: Panel, X) -> str:
    kinds = [P.kind[a] for a in X]
    na = sum(k == "agent" for k in kinds)
    nr = sum(k == "artifact" for k in kinds)
    ne = sum(k == "element" for k in kinds)
    nro = sum(k == "room" for k in kinds)
    if ne and not na and not nr and not nro:
        return "memeplex"
    if na == 1 and not ne and not nro and agents_worth(P, X) == 1:
        return "agent" if nr == 0 else "agent + artifact"
    if not ne and not nro and agents_worth(P, X) >= 2:
        return "agents"
    if na == 0 and nr and not ne and not nro:
        return "artifacts"
    return "mixed"


def agents_worth(P: Panel, X) -> int:
    """Distinct agents represented: agent atoms plus owners of artifact atoms."""
    s = set()
    for a in X:
        if P.kind[a] == "agent":
            s.add(int(P.agent_of[a]))
        elif P.kind[a] == "artifact":
            s.add(int(P.owner[a]))
    return len(s)


def integration(ev: Evaluator, X, hc: int, he: int, lam: float = 1.0) -> dict:
    """Delta = L(x' | parts, E) - L(x' | x, E), held-out bits (individuality.delta_integration, ridge logit)."""
    P = ev.P
    sym = ev.coarse(ev.codes([tuple(X)]), hc)[0]
    E = ev.env([tuple(X)])[0]
    t = ev.tr[he]
    b0 = P.b0[t]
    yn = sym[b0 + 1]
    Sc = IND.onehot(sym[b0], KX)
    parts = np.hstack([IND.onehot(P.S[a, b0].astype(np.int64), int(P.K[a])) for a in X])
    Eb = IND.onehot(E[b0], KE)
    return IND.delta_integration(yn, Sc, parts, Eb, P.tday[t], KX, lam=lam)


# ============================================================================== verification
def verify(P: Panel | None = None) -> bool:
    """The batched evaluator equals individuality.krakauer_discrete on random systems."""
    P = load_panel(30, with_elements=False) if P is None else P
    ev = Evaluator(P)
    rng = np.random.default_rng(1)
    systems = [tuple(sorted(rng.choice(P.nA, size=k, replace=False).tolist())) for k in (1, 2, 3, 4) for _ in range(3)]
    sc = ev.score(systems, 0, hes=(1,))
    ok = True
    for h in (0, 1):
        t = ev.tr[h]
        b0 = P.b0[t]
        for j, X in enumerate(systems):
            M = ev.pres_mask([X])
            sym = ev.coarse(ev.codes([X]), 0, M)[0]
            E = ev.env([X])[0]
            k = M[0, b0] & M[0, b0 + 1]
            bb = b0[k]
            r = IND.krakauer_discrete(sym[bb + 1], sym[bb], E[bb], P.tday[t][k], KX, KE)
            if not r.get("ok") or k.sum() < MIN_TRANS:
                if not np.isnan(sc[h]["A"][j]):
                    ok = False
                    print("expected nan", h, X)
                continue
            for q, q2 in (("A", "A"), ("nC", "nC"), ("Astar", "A_star")):
                if abs(r[q2] - sc[h][q][j]) > 1e-9:
                    ok = False
                    print("mismatch", h, X, q, r[q2], sc[h][q][j])
    print("verify", "ok" if ok else "FAILED")
    return ok


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
