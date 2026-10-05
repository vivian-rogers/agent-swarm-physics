"""H13 round 2 library (card: "Round 2"). Plain-array estimators shared by r2_synthetic.py and the real runs.

R2-A  graded style ladder: feature blocks (S20, core14, FW50, genre G), genre control with agent fixed effects (H46's
      method, reimplemented), within-agent (W) and pooled (P) style maps, family field T on the residuals (round-1 a1).
R2-B  enculturation: statement-count-matched lab alignment a(d) and room outsiderness r(d) of joiners.
R2-C  read-out family coupling: H50's matched-age hop-1 vs hop-0 content jump (reimplemented from shared tables), split
      by same-lab vs cross-lab rows and named vs unnamed rows; talk response at the read-out call.
"""
from __future__ import annotations

import os
for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h13lib as L  # noqa: E402

SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
DATA = ROOT / "data/processed/H13-family-fields"
R2 = DATA / "r2"
STYLE = ["log_chars", "lines", "bullet_share", "headers", "bold", "emoji", "excl", "ques", "urls", "backticks",
         "digit_share", "upper_share", "at", "emdash", "fps", "fpp", "sp", "colon", "word_len", "parens"]
CORE14 = [f for f in STYLE if f not in ("log_chars", "urls", "backticks", "digit_share", "upper_share", "colon")]
GENRE = ["is_reply", "par_human", "par_auto", "p_supports", "p_opposes", "p_asks", "p_reply_max", "has_ment", "log_ment",
         "lead_at", "p_plan_coordinate", "p_research_browse", "p_communicate_external", "p_debug_recover",
         "p_verify_report", "p_monitor_wait", "p_self_maintenance", "p_social", "p_meta", "p_idle",
         "p_addresses_participant", "p_blocked", "dq3_missing"]
COUNTED = ["35", "36b", "37", "38a", "38b", "38c", "39", "40", "41", "42", "44", "51a", "51b", "51c", "51d"]
DESCRIPTIVE = ["51e"]
GDIR = {"35": "G35", "36b": "G36", "37": "G37", "38a": "G38", "38b": "G38", "38c": "G38", "39": "G39", "40": "G40",
        "41": "G41", "42": "G42", "44": "G44", "51a": "G51", "51b": "G51", "51c": "G51", "51d": "G51", "51e": "G51"}
MODELS = {"bge": "bge_small", "gte": "gte_modernbert"}


def unitv(X):
    X = np.asarray(X, np.float64)
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(n > 0, n, 1)


def zs(X):
    X = np.nan_to_num(np.asarray(X, np.float64))
    sd = X.std(0)
    return (X - X.mean(0)) / np.where(sd > 1e-12, sd, 1.0)


# ============================================================================ R2-A data
def load_stmts(u):
    return pl.read_parquet(R2 / "stmts" / f"u{u}.parquet")


def vectors(t: pl.DataFrame, model="bge", kind="white32"):
    sfx = MODELS[model]
    f = {"white32": f"statements_white32_{sfx}.npy", "srp": f"statements_style_resid_period32_{sfx}.npy"}[kind]
    A = np.load(ED / f, mmap_mode="r")
    return unitv(np.asarray(A[t["srow"].to_numpy()], np.float64))


def agent_demean(M, inv, cnt):
    S = np.zeros((cnt.size, M.shape[1]))
    np.add.at(S, inv, M)
    return M - (S / cnt[:, None])[inv]


def genre_control(X, G, inv, cnt):
    """H46 method: B from agent-demeaned X on agent-demeaned G; remove (G - mean G) B only (agent constant kept)."""
    keep = G.std(0) > 1e-9
    Gk = G[:, keep]
    B, *_ = np.linalg.lstsq(agent_demean(Gk, inv, cnt), agent_demean(X, inv, cnt), rcond=None)
    return X - (Gk - Gk.mean(0)) @ B


def blocks(t: pl.DataFrame):
    """Standardized feature blocks for one unit. Returns dict name -> (n x p) array, plus inv/cnt (agent index)."""
    ag = t["agent"].to_numpy()
    _, inv = np.unique(ag, return_inverse=True)
    cnt = np.bincount(inv).astype(float)
    S20 = zs(t.select([f"f_{k}" for k in STYLE]).to_numpy())
    C14 = zs(t.select([f"f_{k}" for k in CORE14]).to_numpy())
    W = t.select([c for c in t.columns if c.startswith("w_")]).to_numpy().astype(np.float64)
    short = t["short"].to_numpy().astype(float)
    lo, hi = np.nanquantile(W, 0.001, axis=0), np.nanquantile(W, 0.999, axis=0)
    W = np.clip(W, lo, hi)
    mu, sd = np.nanmean(W, 0), np.nanstd(W, 0)
    W = np.where(np.isnan(W), 0.0, (W - mu) / np.where(sd > 1e-12, sd, 1.0))
    FW = np.column_stack([W, zs(short[:, None])])
    G = zs(t.select(GENRE).to_numpy())
    out = {"S20": S20, "core14": C14, "FW50": FW, "G": G}
    out["S20g"] = genre_control(S20, G, inv, cnt)
    out["core14g"] = genre_control(C14, G, inv, cnt)
    out["FW50g"] = genre_control(FW, G, inv, cnt)
    return out, inv, cnt


LEVELS = {  # name: (map, block list)
    "L0": (None, []),
    "W1": ("W", ["core14g"]), "W2": ("W", ["S20g"]), "W3": ("W", ["S20g", "FW50g"]), "Wf": ("W", ["FW50g"]),
    "P1": ("P", ["core14g"]), "P2": ("P", ["S20g"]), "P3": ("P", ["S20g", "FW50g"]), "Pf": ("P", ["FW50g"]),
    "S-a": ("P", ["S20"]), "S-a'": ("W", ["S20"]), "PG": ("P", ["G"]),
}


def map_resid(U, X, inv, cnt, kind):
    """Residual statement vectors (renormalized) and the share of statement-vector variance the map removes."""
    if kind is None:
        return U, 0.0
    if kind == "W":
        B, *_ = np.linalg.lstsq(agent_demean(X, inv, cnt), agent_demean(U, inv, cnt), rcond=None)
        R = U - (X - X.mean(0)) @ B
    else:
        X1 = np.column_stack([np.ones(len(X)), X])
        B, *_ = np.linalg.lstsq(X1, U, rcond=None)
        R = U - X1 @ B
    tot = ((U - U.mean(0)) ** 2).sum()
    r2 = float(1 - ((R - R.mean(0)) ** 2).sum() / tot)
    return unitv(R), r2


class UnitSkel:
    """Index structure for the a1 pipeline on one unit's statements (agent-day means >= 3, day-demean, >= 2 days)."""

    def __init__(self, t: pl.DataFrame, lab_of: dict, min_n=3):
        ag = t["agent"].to_numpy().astype(int)
        dd = t["pt_date"].to_numpy()
        key = np.array([f"{a}|{d}" for a, d in zip(ag, dd)])
        uk, kinv = np.unique(key, return_inverse=True)
        n = np.bincount(kinv)
        self.kinv, self.n = kinv, n
        self.ad_agent = np.array([int(k.split("|")[0]) for k in uk])
        self.ad_day = np.array([k.split("|")[1] for k in uk])
        self.ok = n >= min_n
        # agents with >= 2 eligible days after day-demeaning on days with >= 3 eligible agents
        A, D = self.ad_agent[self.ok], self.ad_day[self.ok]
        dok = np.zeros(len(A), bool)
        for d in np.unique(D):
            k = D == d
            if k.sum() >= 3:
                dok[k] = True
        self.dok = dok
        ags = [a for a in np.unique(A[dok]) if (A[dok] == a).sum() >= 2]
        self.ags = np.array(ags)
        labs = [lab_of[a] for a in self.ags]
        self.labs = labs
        self.fam, self.multi = L.fam_labels(labs)
        self.K = len(self.multi)
        roles = dict(zip(t["agent"].to_list(), t["role"].to_list()))
        n_ = len(self.ags)
        keep = np.ones((n_, n_), bool)
        for i in range(n_):
            for j in range(n_):
                ri, rj = roles.get(self.ags[i]), roles.get(self.ags[j])
                if i != j and ri is not None and ri == rj:
                    keep[i, j] = False
        self.keep = keep if not keep.all() else None

    def agent_fields(self, Uv, lfo=False):
        """H (n_agents x d) of day-demeaned agent-day means. lfo: leave-family-out day mean (multi-member labs)."""
        S = np.zeros((len(self.n), Uv.shape[1]))
        np.add.at(S, self.kinv, Uv)
        V = (S / self.n[:, None])[self.ok]
        A, D = self.ad_agent[self.ok], self.ad_day[self.ok]
        lab = np.array([self.labs_of_agent(a) for a in A])
        Dm = np.full_like(V, np.nan)
        for d in np.unique(D[self.dok]):
            k = (D == d) & self.dok
            if not lfo:
                Dm[k] = V[k] - V[k].mean(0)
            else:
                for i in np.where(k)[0]:
                    o = k & (lab != lab[i]) if lab[i] is not None else k
                    Dm[i] = V[i] - V[o].mean(0)
        H = np.array([np.nanmean(Dm[(A == a) & self.dok], 0) for a in self.ags])
        return H

    def labs_of_agent(self, a):
        idx = np.where(self.ags == a)[0]
        if len(idx) == 0:
            return None
        f = self.fam[idx[0]]
        return int(f) if f < self.K else None

    def T(self, H, nperm=2000, rng=None, jack=True):
        return L.field_test(H, self.fam, self.K, keep_pairs=self.keep, nperm=nperm, rng=rng, jack=jack)


def agent_mean_vectors(X, t, ags):
    ag = t["agent"].to_numpy()
    return np.array([X[ag == a].mean(0) for a in ags])


def ladder_unit(U, blk, inv, cnt, sk: UnitSkel, levels=LEVELS, nperm=2000, rng=None, jack=True, lfo=()):
    out = {}
    for name, (kind, bl) in levels.items():
        X = np.hstack([blk[b] for b in bl]) if bl else None
        R, r2 = map_resid(U, X, inv, cnt, kind)
        H = sk.agent_fields(R)
        ft = sk.T(H, nperm=nperm, rng=rng, jack=jack)
        out[name] = {"T": ft["obs"], "p": ft["p"], "se": ft.get("se_jack", np.nan), "r2_map": r2}
        if name in lfo:
            H2 = sk.agent_fields(R, lfo=True)
            f2 = sk.T(H2, nperm=nperm, rng=rng, jack=jack)
            out[name + "_lfo"] = {"T": f2["obs"], "p": f2["p"], "se": f2.get("se_jack", np.nan)}
    return out


def re_summary(per_unit: dict, units, level):
    est = [per_unit[u][level]["T"] for u in units]
    se = [per_unit[u][level]["se"] for u in units]
    return L.dl_meta(est, se)


def roster_labs():
    r = pl.read_parquet(SH / "roster.parquet", columns=["agent", "lab", "name"])
    return dict(zip(r["agent"].to_list(), r["lab"].to_list())), dict(zip(r["agent"].to_list(), r["name"].to_list()))


def clean(o):
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return clean(o.tolist())
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def dump(obj, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(clean(obj), indent=1))
