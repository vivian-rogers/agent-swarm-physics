"""H37 data access: reply pairs + Jev labels + relation labels per goal period (codes only, no text).

  load_pairs(g)        pairs (all kinds; #12 includes the Amendment-1 debater pairs) joined to Jev labels if present
  g12_relations(df)    debate index, phase (pre / deb / post), relation (same / opposite / judge / bench / none)
  g51_roles(df)        per-reply pair class from the day's roles (H22 role_relations), and per-agent majority role
  g26_votes()          H11's first-person declared vote sets (codes only)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
H37 = HERE.parent
ROOT = H37.parents[1]
DATA = ROOT / "data/processed/H37-stance-spins"
SHARED = ROOT / "data/processed/shared"
sys.path.insert(0, str(H37 / "scheme"))
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H22-private-goals-spin-glass/scheme"))
from select_samples import debate_windows, UNITS51  # noqa: E402
import role_relations as RR  # noqa: E402

STANCES = ["agree", "support", "neutral", "oppose", "undermine"]
SIGN = {"agree": 1, "support": 1, "neutral": 0, "oppose": -1, "undermine": -1}


def load_labels(g):
    rows = []
    for f in sorted((DATA / "labels").glob(f"G{g:02d}_*.jsonl")):
        if "smoke" in f.name:
            continue
        for line in f.open():
            j = json.loads(line)
            if j.get("stance") is None:
                continue
            rows.append({k: j.get(k) for k in ["pair_id", "stance", "stance_conf", "p_agree", "p_support", "p_neutral", "p_oppose",
                                               "p_undermine", "responds", "cost"]})
    if not rows:
        return None
    L = pl.DataFrame(rows, infer_schema_length=None).unique("pair_id", keep="last")
    L = L.with_columns((pl.col("p_agree") + pl.col("p_support") - pl.col("p_oppose") - pl.col("p_undermine")).alias("s_soft"),
                       pl.col("stance").replace_strict(SIGN, return_dtype=pl.Int8).alias("s_hard"))
    return L


def load_pairs(g, labelled_only=True):
    P = pl.read_parquet(DATA / f"pairs/G{g:02d}.parquet")
    if g == 12 and (DATA / "pairs/G12_debater.parquet").exists():
        P = pl.concat([P, pl.read_parquet(DATA / "pairs/G12_debater.parquet")])
    L = load_labels(g)
    if L is not None:
        P = P.join(L, on="pair_id", how="inner" if labelled_only else "left")
    return P


def g12_relations(P):
    """Debate, phase and relation per pair (B's time decides the debate and phase; A must be inside the window)."""
    names = dict(pl.read_parquet(SHARED / "roster.parquet", columns=["name", "agent"]).iter_rows())
    W = debate_windows()
    tb = P["t_b"].to_list(); ta = P["t_a"].to_list(); aa = P["agent_a"].to_list(); ab = P["agent_b"].to_list()
    deb, phase, rel = [], [], []
    for k in range(P.height):
        d, ph, r = -1, "none", "none"
        for w in W:
            if w["pre_start"] <= tb[k] < w["post_end"] and ta[k] >= w["pre_start"]:
                d = w["debate"]
                ph = "pre" if tb[k] < w["first_speech"] else ("deb" if tb[k] < w["verdict"] else "post")
                gov = {names[x] for x in w["gov"]}; opp = {names[x] for x in w["opp"]}
                judge = names[w["judge"]]; bench = {names[x] for x in w["bench"]}
                i, j = aa[k], ab[k]
                if judge in (i, j):
                    r = "judge"
                elif (i in gov and j in gov) or (i in opp and j in opp):
                    r = "same"
                elif (i in gov and j in opp) or (i in opp and j in gov):
                    r = "opposite"
                elif i in bench or j in bench:
                    r = "bench"
                break
        deb.append(d); phase.append(ph); rel.append(r)
    return P.with_columns(pl.Series("debate", deb, pl.Int16), pl.Series("phase", phase), pl.Series("rel", rel))


def g12_teams():
    """{debate: {agent: +1 gov / -1 opp}}, judge, sizes."""
    names = dict(pl.read_parquet(SHARED / "roster.parquet", columns=["name", "agent"]).iter_rows())
    out = {}
    for w in debate_windows():
        t = {names[x]: 1 for x in w["gov"]}
        t.update({names[x]: -1 for x in w["opp"]})
        out[w["debate"]] = {"team": t, "judge": names[w["judge"]], "bench": [names[x] for x in w["bench"]]}
    return out


def _roster_ids():
    r = pl.read_parquet(SHARED / "roster.parquet")
    return dict(zip(r["agent_id"].to_list(), r["agent"].to_list()))


def g51_roles(P):
    """Per-reply pair class from the day's roles; plus the H22 unit."""
    sp = RR.load_role_spells(_roster_ids())
    cache = {}

    def role(a, d):
        if (a, d) not in cache:
            cache[(a, d)] = RR.role_on(sp, a, d)
        return cache[(a, d)]
    ra = [role(a, d) for a, d in zip(P["agent_a"].to_list(), P["pt_date"].to_list())]
    rb = [role(b, d) for b, d in zip(P["agent_b"].to_list(), P["pt_date"].to_list())]
    cls = [RR.pair_class(x, y) for x, y in zip(ra, rb)]
    unit = pl.lit(None, pl.String)
    for u, (a, b) in UNITS51.items():
        unit = pl.when((pl.col("pt_date") >= a) & (pl.col("pt_date") <= b)).then(pl.lit(u)).otherwise(unit)
    return P.with_columns(pl.Series("role_a", ra), pl.Series("role_b", rb), pl.Series("cls", cls, pl.Int8), unit.alias("unit"))


def g51_majority_roles(agents, days_by_agent):
    sp = RR.load_role_spells(_roster_ids())
    out = {}
    for a in agents:
        rs = [RR.role_on(sp, a, d) for d in days_by_agent[a]]
        known = [r for r in rs if r is not None]
        if len(known) * 2 >= max(1, len(rs)):
            v, c = np.unique(known, return_counts=True)
            out[a] = str(v[np.argmax(c)])
        else:
            out[a] = None
    return out


def g26_votes():
    v = pl.read_parquet(ROOT / "data/processed/H11-potts-labor-vs-herding/G26/votes.parquet")
    return v.filter(pl.col("vote_word") & (pl.col("n_named") > 0) & pl.col("first_person")).sort("t")


def labs():
    return dict(pl.read_parquet(SHARED / "roster.parquet", columns=["agent", "lab"]).iter_rows())


def names():
    return dict(pl.read_parquet(SHARED / "roster.parquet", columns=["agent", "name"]).iter_rows())


def record(name, built_by, params=None, tables=None):
    """Add or replace an entry in data/processed/H37-stance-spins/_provenance.json."""
    import datetime as dt
    from common import REVISION, git_commit
    path = DATA / "_provenance.json"
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov[name] = {"built_by": built_by, "git_commit": git_commit(),
                  "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables or ["H37 pairs + Jev labels (codes only)"]}],
                  "params": params or {}, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    path.write_text(json.dumps(prov, indent=1, default=str))
