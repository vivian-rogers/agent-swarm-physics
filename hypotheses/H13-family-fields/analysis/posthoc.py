"""H13 round-1 POST HOC diagnostics (written after seeing explore.json; labeled post hoc in the card).

Motivation: the pre-registered style rival S-a (within-unit statement-level OLS of whitened statement vectors on 20
style features) removed the family field in every unit. With 20 features and 10-27 agents, a statement-level
regression can absorb agent-level offsets through the between-agent variation of the features, so S-a may remove
family *position* as well as style. Diagnostics:
  D1  does S-a also remove the ROOM field (y2 b_room on residualized vectors, two-room units)? A selective style
      removal should leave room fields (room-specific tasks) intact.
  D2  S-a': style map B estimated from WITHIN-agent variation only (agent-demeaned statements and features), then
      applied to the raw features; T_field and y2 b_lab / b_room on the residuals.
  D3  family structure of the agents' mean style-feature vectors alone (no embeddings): T_style-features, LOO.
  D4  per-family within-family mean cosine (raw H), to see which families carry the field.

Usage: uv run python hypotheses/H13-family-fields/analysis/posthoc.py
Writes data/processed/H13-family-fields/posthoc.json.
"""
from __future__ import annotations

import json
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
NP = 2000


def statement_level(u, spec):
    """Rebuild unit statements: unit-normalized whitened vectors U, standardized style features F, agent, pt_date."""
    gdir, goal, reg, a, b = spec
    days = B.unit_days(spec)
    st = pl.read_parquet(B.ED / "statements.parquet").filter((pl.col("kind") == "chat") & pl.col("pt_date").is_in(days))
    cidx = pl.read_parquet(B.ED / "chat_index.parquet").with_row_index("src_row")
    s = st.join(cidx, on="src_row", how="left").sort("t")
    txt = pl.read_parquet(B.SH / "chat_text.parquet", columns=["message_id", "text"]).join(s.select("message_id"), on="message_id", how="semi")
    s = s.join(B.text_features(txt), on="message_id", how="left")
    Ec = np.load(B.ED / "chat_bge_small.npy", mmap_mode="r")
    Z = B.load_whitener(reg, B.DIM)(np.asarray(Ec[s["src_row"].to_numpy()], dtype=np.float32))
    U = Z / np.linalg.norm(Z, axis=1, keepdims=True)
    F = np.nan_to_num(s.select([f"f_{k}" for k in B.STYLE]).to_numpy().astype(np.float64))
    F = (F - F.mean(0)) / np.where(F.std(0) > 0, F.std(0), 1)
    return U.astype(np.float64), F, s["agent"].to_numpy(), s["pt_date"].to_numpy()


def agent_day_means(U, agent, day, min_n=3):
    keys = {}
    for k, (a, d) in enumerate(zip(agent, day)):
        keys.setdefault((a, d), []).append(k)
    rows = [(a, d, ix) for (a, d), ix in keys.items() if len(ix) >= min_n]
    V = np.array([U[ix].mean(0) for _, _, ix in rows])
    return V, np.array([r[0] for r in rows]), np.array([r[1] for r in rows])


def fields_from(V, ag, dd):
    D = L.day_demean(V, dd, ag)
    return L.agent_means(D, ag)


def main():
    t0 = time.time()
    rng = np.random.default_rng(20261005)
    meta = json.loads((DATA / "units.json").read_text())
    lab_of, name_of = E.roster()
    out = {}
    for u in E.COUNTED + E.DESCRIPTIVE:
        spec = B.UNITS[u]
        U, F, ag_s, dd_s = statement_level(u, spec)
        res = {}
        # S-a (pre-registered) reproduced, and S-a' (within-agent style map)
        X = np.column_stack([np.ones(len(F)), F])
        Bfull = np.linalg.lstsq(X, U, rcond=None)[0]
        R_sa = U - X @ Bfull
        Fw = F.copy(); Uw = U.copy()
        for a in np.unique(ag_s):
            k = ag_s == a
            Fw[k] -= Fw[k].mean(0); Uw[k] -= Uw[k].mean(0)
        Bw = np.linalg.lstsq(Fw, Uw, rcond=None)[0]
        R_saw = U - F @ Bw
        res["style_r2_within"] = float(1 - ((Uw - Fw @ Bw) ** 2).sum() / (Uw ** 2).sum())
        variants = {"raw": U, "S-a": L.unit(R_sa), "S-a_within": L.unit(R_saw)}
        Hs = {}
        for name, M in variants.items():
            V, ag, dd = agent_day_means(M, ag_s, dd_s)
            ags, H, _ = fields_from(V, ag, dd)
            Hs[name] = (ags, H)
        ags0 = Hs["raw"][0]
        labs = [lab_of[a] for a in ags0]
        fam, multi = L.fam_labels(labs)
        K = len(multi)
        roles = meta[u].get("roles", {})
        keep = E.role_keep(ags0, roles) if roles else None
        for name, (ags, H) in Hs.items():
            assert np.array_equal(ags, ags0)
            ft = L.field_test(H, fam, K, keep_pairs=keep, nperm=NP, rng=rng, jack=False)
            res[f"T_{name}"] = {"obs": ft["obs"], "p": ft["p"]}
        # D1/D2: family vs room on each variant
        if u in E.TWO_ROOM:
            ad = pl.read_parquet(DATA / meta[u]["gdir"] / f"u{u}_agent_day.parquet")
            rooms = E.agent_rooms(ad, ags0)
            for name, (ags, H) in Hs.items():
                Y = L.unit(H) @ L.unit(H).T
                fr = L.famroom(Y, fam, rooms, K, nperm=NP, rng=rng, jack=False)
                res[f"y2_{name}"] = {k: fr[k] for k in ("b_lab", "p_lab", "b_room", "p_room")}
        # D3: style features alone (agent mean standardized feature vector over the unit's statements)
        Fa = np.array([F[ag_s == a].mean(0) for a in ags0])
        ft = L.field_test(Fa, fam, K, keep_pairs=keep, nperm=NP, rng=rng, jack=False)
        res["T_stylefeatures"] = {"obs": ft["obs"], "p": ft["p"]}
        res["loo_stylefeatures"] = L.loo_perm(Fa, fam, K, nperm=NP // 2, rng=rng)
        # D4: per-family within-family mean cosine vs across mean (raw)
        H = Hs["raw"][1]
        C = L.unit(H) @ L.unit(H).T
        ii, jj = L.pairs(len(H))
        across = C[ii, jj][fam[ii] != fam[jj]].mean()
        res["within_by_family"] = {multi[k]: float(C[ii, jj][(fam[ii] == k) & (fam[jj] == k)].mean()) for k in range(K)}
        res["across_mean"] = float(across)
        out[u] = res
        print(u, {k: (v if not isinstance(v, dict) else {kk: round(vv, 3) if isinstance(vv, float) else vv for kk, vv in v.items()})
                  for k, v in res.items() if k != "loo_stylefeatures"}, flush=True)
    # summaries
    cu = E.COUNTED
    summ = {}
    for name in ("raw", "S-a", "S-a_within"):
        summ[f"T_{name}_sig"] = int(sum(out[u][f"T_{name}"]["p"] < 0.05 for u in cu))
        summ[f"T_{name}_median"] = float(np.median([out[u][f"T_{name}"]["obs"] for u in cu]))
        tr = [u for u in cu if u in E.TWO_ROOM]
        summ[f"y2_{name}_lab_sig"] = int(sum(out[u][f"y2_{name}"]["p_lab"] < 0.05 for u in tr))
        summ[f"y2_{name}_room_sig"] = int(sum(out[u][f"y2_{name}"]["p_room"] < 0.05 for u in tr))
        summ[f"y2_{name}_b_lab_median"] = float(np.median([out[u][f"y2_{name}"]["b_lab"] for u in tr]))
        summ[f"y2_{name}_b_room_median"] = float(np.median([out[u][f"y2_{name}"]["b_room"] for u in tr]))
    summ["T_stylefeatures_sig"] = int(sum(out[u]["T_stylefeatures"]["p"] < 0.05 for u in cu))
    summ["loo_stylefeatures_sig"] = int(sum(out[u]["loo_stylefeatures"]["p"] < 0.05 for u in cu))
    fams = {}
    for u in cu:
        for f, v in out[u]["within_by_family"].items():
            fams.setdefault(f, []).append(v - out[u]["across_mean"])
    summ["within_minus_across_by_family_median"] = {f: [float(np.median(v)), len(v)] for f, v in fams.items()}
    out["_summary"] = summ
    out["_seconds"] = round(time.time() - t0, 1)
    print(json.dumps(summ, indent=1))
    (DATA / "posthoc.json").write_text(json.dumps(E.clean(out), indent=1))


if __name__ == "__main__":
    main()
