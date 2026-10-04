"""H22 scheme: builds data/processed/H22-private-goals-spin-glass/G<NN>/<unit>/ from the shared tables (card, Data scheme).

Per unit (goal period split at step changes; same units as H01/H13):
  win_index.parquet + win_vec.npy    agent x day x 30-min window: mean of whitened (regime III, n = 32), unit-normalized
                                     own-chat statement vectors; n statements (float16 vectors)
  day_index.parquet + day_vec.npy    agent x day: [full, first half, second half] means (time-split halves; >= 3 stmts)
  talk.npz                           per-day talk-spin correlations c[d,i,j], cross-day surrogate cs[d,e,i,j]; and the
                                     day-thirds (pseudo-day) versions c3 / cs3 for short units
  agents.parquet                     unit agent index -> roster code, name, lab, modal room + purity, #51 role
  meta.json                          days, windows per day, counts
No text is written. Holdout days are refused unless build_unit(..., allow_holdout=True) is called by the
confirmatory script (which itself requires its flags).

Usage: uv run python hypotheses/H22-private-goals-spin-glass/scheme/build.py
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT as SHARED, REVISION, git_commit, holdout_mask, load_whitener  # noqa: E402
import role_relations as RR  # noqa: E402

DATA = ROOT / "data/processed/H22-private-goals-spin-glass"
ED = SHARED / "embeddings"

UNITS = {
    "51a": ("G51", "2026-07-06", "2026-07-08"), "51b": ("G51", "2026-07-09", "2026-08-04"),
    "51c": ("G51", "2026-08-05", "2026-08-24"), "51d": ("G51", "2026-08-25", "2026-09-02"),
    "51e": ("G51", "2026-09-03", "2026-09-04"),
    "38a": ("G38", "2026-04-02", "2026-04-13"), "38b": ("G38", "2026-04-14", "2026-04-17"),
    "38c": ("G38", "2026-04-20", "2026-04-24"),
    "40": ("G40", "2026-05-04", "2026-05-08"), "44": ("G44", "2026-05-26", "2026-05-29"),
}
CONFIRM_UNITS = {"51T": ("G51", "2026-09-07", "2026-09-18")}  # locked holdout: confirm_tail.py only


def unit_days(a, b):
    cal = pl.read_parquet(SHARED / "calendar.parquet")
    c = cal.filter((pl.col("pt_date") >= a) & (pl.col("pt_date") <= b) & (pl.col("n_agent_events") > 0)).sort("pt_date")
    return c


def talk_arrays(ab_days, agents, days, thirds=False):
    """Per-(pseudo-)day talk-spin correlation matrices and the cross-(pseudo-)day surrogate."""
    N = len(agents)
    aidx = {a: k for k, a in enumerate(agents)}
    series = []  # list of [N, T] arrays with NaN rows for absent agents
    for d in days:
        t = ab_days.filter(pl.col("pt_date") == d)
        T = int(t["minute"].max()) + 1 if t.height else 0
        S = np.full((N, T), np.nan)
        for a, m, st in t.select("agent", "minute", "state").iter_rows():
            if a in aidx:
                S[aidx[a], m] = 1.0 if st == 4 else -1.0
        S[np.isnan(S) & ~np.all(np.isnan(S), axis=1, keepdims=True)] = -1.0  # missing minutes of present agents: silent
        if thirds:
            b = [0, T // 3, 2 * T // 3, T]
            series += [S[:, b[k]:b[k + 1]] for k in range(3)]
        else:
            series.append(S)
    Dp = len(series)

    def zs(S):
        ok = ~np.all(np.isnan(S), 1) & (np.nansum(S > 0, 1) >= 4)
        Z = np.where(ok[:, None], S, 0.0)
        mu = Z.mean(1, keepdims=True); sd = Z.std(1, keepdims=True)
        Z = np.where(ok[:, None] & (sd > 0), (Z - mu) / np.where(sd > 0, sd, 1), 0.0)
        return Z, ok & (sd[:, 0] > 0)

    c = np.full((Dp, N, N), np.nan)
    cs = np.full((Dp, Dp, N, N), np.nan)
    for d in range(Dp):
        Z, ok = zs(series[d])
        if Z.shape[1] < 10:
            continue
        M = Z @ Z.T / Z.shape[1]
        M[~(ok[:, None] & ok[None, :])] = np.nan
        np.fill_diagonal(M, np.nan)
        c[d] = M
    for d in range(Dp):
        for e in range(Dp):
            if d == e:
                continue
            T = min(series[d].shape[1], series[e].shape[1])
            if T < 10:
                continue
            Zd, okd = zs(series[d][:, :T]); Ze, oke = zs(series[e][:, :T])
            M = Zd @ Ze.T / T
            M[~(okd[:, None] & oke[None, :])] = np.nan
            cs[d, e] = M
    return c.astype(np.float32), cs.astype(np.float32)


def build_unit(name, allow_holdout=False, units=None):
    units = units or {**UNITS, **CONFIRM_UNITS}
    period, a, b = units[name]
    cal = unit_days(a, b)
    days = cal["pt_date"].to_list()
    held = holdout_mask(days, cal["goal_no"].to_list())
    if any(held) and not allow_holdout:
        raise SystemExit(f"unit {name} contains locked-holdout days; refusing (confirm_tail.py only)")
    if not allow_holdout and name in CONFIRM_UNITS:
        raise SystemExit(f"unit {name} is the locked holdout; refusing")
    t0 = time.time()
    out = DATA / period / name
    out.mkdir(parents=True, exist_ok=True)
    wpd = [int(math.ceil(w / 1800)) for w in cal["window_s"].to_list()]
    dix = {d: k for k, d in enumerate(days)}

    st = (pl.read_parquet(ED / "statements.parquet")
          .filter((pl.col("kind") == "chat") & pl.col("pt_date").is_in(days))
          .sort("t"))
    E = np.load(ED / "chat_bge_small.npy", mmap_mode="r")
    W = load_whitener("III", 32)
    Z = W(np.asarray(E[st["src_row"].to_numpy()], dtype=np.float32))
    Z = Z / np.linalg.norm(Z, axis=1, keepdims=True)
    roster = pl.read_parquet(SHARED / "roster.parquet")
    ab = pl.read_parquet(SHARED / "activity_bins.parquet", columns=["pt_date", "minute", "agent", "state"]).filter(pl.col("pt_date").is_in(days))
    agents = sorted(set(st["agent"].unique().to_list()) | set(ab["agent"].unique().to_list()))
    aidx = {x: k for k, x in enumerate(agents)}
    ag = st["agent"].to_numpy(); dd = np.array([dix[x] for x in st["pt_date"].to_list()])
    w30 = st["win30"].to_numpy()

    # agent-window means
    okw = ~np.isnan(w30.astype(float)) if w30.dtype.kind == "f" else st["win30"].is_not_null().to_numpy()
    keys = {}
    for r in np.flatnonzero(okw):
        keys.setdefault((aidx[ag[r]], dd[r], int(w30[r])), []).append(r)
    wi = sorted(keys)
    wv = np.stack([Z[keys[k]].mean(0) for k in wi]).astype(np.float16) if wi else np.zeros((0, 32), np.float16)
    pl.DataFrame({"a": [k[0] for k in wi], "d": [k[1] for k in wi], "w": [k[2] for k in wi],
                  "n": [len(keys[k]) for k in wi]}).write_parquet(out / "win_index.parquet", compression="zstd")
    np.save(out / "win_vec.npy", wv)

    # agent-day full + time-split halves
    dkeys = {}
    for r in range(st.height):
        dkeys.setdefault((aidx[ag[r]], dd[r]), []).append(r)  # rows already in time order
    di = sorted(dkeys)
    dv = np.zeros((len(di), 3, 32), np.float32)
    for k, key in enumerate(di):
        rr = dkeys[key]
        dv[k, 0] = Z[rr].mean(0)
        if len(rr) >= 2:
            h = len(rr) // 2
            dv[k, 1] = Z[rr[:h]].mean(0); dv[k, 2] = Z[rr[h:]].mean(0)
    pl.DataFrame({"a": [k[0] for k in di], "d": [k[1] for k in di], "n": [len(dkeys[k]) for k in di]}).write_parquet(
        out / "day_index.parquet", compression="zstd")
    np.save(out / "day_vec.npy", dv.astype(np.float16))

    # talk spins
    c, cs = talk_arrays(ab, agents, days)
    c3, cs3 = talk_arrays(ab, agents, days, thirds=True) if len(days) < 7 else (np.zeros(0), np.zeros(0))
    np.savez_compressed(out / "talk.npz", c=c, cs=cs, c3=c3, cs3=cs3)

    # agents: lab, modal room, role
    rmode = (st.group_by("agent", "room").len().sort("len", descending=True).group_by("agent", maintain_order=True)
             .agg(pl.col("room").first().alias("room_mode"), (pl.col("len").first() / pl.col("len").sum()).alias("purity")))
    rm = {x: (r, p) for x, r, p in rmode.iter_rows()}
    rid = dict(zip(roster["agent_id"].to_list(), roster["agent"].to_list()))
    spells = RR.load_role_spells(rid)
    present = {x: sorted({days[k[1]] for k in di if agents[k[0]] == x}) for x in agents}
    roles = RR.unit_roles(spells, agents, days, present) if period == "G51" else {x: None for x in agents}
    ro = roster.filter(pl.col("agent").is_in(agents)).select("agent", "name", "lab")
    trate = dict(ab.group_by("agent").agg((pl.col("state") == 4).mean().alias("r")).iter_rows())
    nwin = {x: 0 for x in agents}
    for k, key in enumerate(wi):
        if len(keys[key]) >= 2:
            nwin[agents[key[0]]] += 1
    adf = (pl.DataFrame({"idx": list(range(len(agents))), "agent": agents}).with_columns(pl.col("agent").cast(pl.Int8))
           .join(ro, on="agent", how="left")
           .with_columns(pl.Series("room_mode", [rm.get(x, (None, None))[0] for x in agents], dtype=pl.Int8),
                         pl.Series("purity", [rm.get(x, (None, None))[1] for x in agents], dtype=pl.Float64),
                         pl.Series("role", [roles.get(x) for x in agents], dtype=pl.String),
                         pl.Series("n_windows", [nwin[x] for x in agents]),
                         pl.Series("n_days", [len(present[x]) for x in agents]),
                         pl.Series("talk_rate", [float(trate.get(x, 0.0)) for x in agents])))
    adf.write_parquet(out / "agents.parquet")
    meta = {"unit": name, "period": period, "days": days, "wins_per_day": wpd, "N_agents": len(agents),
            "n_statements": st.height, "n_windows": len(wi), "n_agent_days": len(di), "holdout": bool(any(held)),
            "built_s": round(time.time() - t0, 1)}
    (out / "meta.json").write_text(json.dumps(meta, indent=1))
    prov_path = DATA / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov[f"{period}/{name}"] = {"built_by": "hypotheses/H22-private-goals-spin-glass/scheme/build.py", "git_commit": git_commit(),
                                "inputs": [{"source": "ai-village", "revision": REVISION,
                                            "tables": ["embeddings/statements", "embeddings/chat_bge_small", "whitening_III",
                                                       "activity_bins", "calendar", "roster", "raw agent_goals"]}],
                                "params": {"whitener": "III", "dim": 32, "win_min": 30, "halves": "time split",
                                           "talk_min_minutes": 4, "days": [a, b]},
                                "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    prov_path.write_text(json.dumps(prov, indent=1))
    print(f"{name}: {len(days)} days, {len(agents)} agents, {st.height} statements, {len(wi)} windows "
          f"({meta['built_s']}s)", flush=True)
    return meta


def main():
    for name in UNITS:
        build_unit(name)


if __name__ == "__main__":
    main()
