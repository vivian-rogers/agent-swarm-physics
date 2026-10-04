"""H42 POST HOC (added 2026-10-04 after reading the interim replication results): does a message that NAMES the
recipient excite its talk at read-out, when unnamed messages do not?

Motivation: in the coherent call-clock world (world B) the read-out kernel's n_cross is ~0 for talk, while H08 found
that *addressing* the sender jumps at the read-out turn and H29 that naming pulls the next statement 3-6x. If messages
steer what agents say rather than whether they talk, unnamed messages should carry ~0 talk excitation; named ones may
carry some (a direct request).

World B design; B columns split by the ledger's `ment` flag (message names the recipient): Bm_* (named) and Bu_*
(unnamed), call-index bins as B. Fits S0, B (unsplit), Bmu (split); day-blocked CV; 3 shift surrogates (in sample)
for Bmu. Writes data/processed/H42-readout-hawkes-kernel/posthoc_mention.parquet.
"""
from __future__ import annotations

import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h42lib as L  # noqa: E402


def split_items(items: pl.DataFrame, named: bool) -> pl.DataFrame:
    return items.filter((pl.col("kind") == "agent") & (pl.col("ment") == named))


def design(u: L.Unit, items=None):
    base = L.build_talk(u, world="B", specs=())
    it = u.items if items is None else items
    cols, names, Zs = [base.F], list(base.names), [base.Zd]
    for tag, named in (("Bm", True), ("Bu", False)):
        sub = split_items(it, named)
        d = L.build_talk(u, world="B", items_override=sub, only_cross=True, base=None, specs=("B",))
        k = [i for i, nm in enumerate(d.names) if nm.startswith("B_")]
        cols.append(d.F[:, k]); Zs.append(d.Zd[:, k]); names += [f"{tag}_{d.names[i].split('_')[1]}" for i in k]
    # unsplit B for comparison
    d = L.build_talk(u, world="B", items_override=it.filter(pl.col("kind") == "agent"), only_cross=True, specs=("B",))
    k = [i for i, nm in enumerate(d.names) if nm.startswith("B_")]
    cols.append(d.F[:, k]); Zs.append(d.Zd[:, k]); names += [d.names[i] for i in k]
    base.F = np.column_stack(cols); base.Zd = np.column_stack(Zs); base.names = names
    return base


SPECS = {"S0": L.W_BASE, "B": L.W_BASE + ("B",), "Bmu": L.W_BASE + ("Bm", "Bu")}


def run(uid):
    goal = int("".join(ch for ch in uid if ch.isdigit()))
    return run_unit(L.load_unit(uid, goal))


def run_unit(u: L.Unit):
    uid = u.unit_id
    ds = design(u)
    out = {"unit_id": uid, "regime": u.regime, "n_days": u.n_days, "n_events": ds.meta["n_events"],
           "n_named_items": int(u.items.filter((pl.col("kind") == "agent") & pl.col("ment")).height),
           "n_items": int(u.items.filter(pl.col("kind") == "agent").height)}
    fits = {}
    for s in SPECS:
        f = L.fit_spec(ds, SPECS, s, warm=fits.get("S0"))
        fits[s] = f
        br = L.branching(ds, f)
        out[f"{s}:ll"] = f.ll
        out[f"{s}:nx"] = br["n_cross"]
        if s == "Bmu":
            out["n_named"] = br.get("n_Bm", 0.0)
            out["n_unnamed"] = br.get("n_Bu", 0.0)
            w = br["weights"]
            out["w_named_0"] = w.get("Bm_0", 0.0)
            out["w_unnamed_0"] = w.get("Bu_0", 0.0)
    if u.n_days >= 2:
        cvr = L.cv(ds, SPECS, list(SPECS))
        for s, (ll, n) in cvr.items():
            out[f"{s}:cv"] = ll / max(n, 1)
    rng = np.random.default_rng(7)
    nn, nu = [], []
    for _ in range(3):
        items, _k = L.shift_items(u, rng)
        dn = design(u, items=pl.concat([u.items.filter(pl.col("kind") != "agent"), items.select(u.items.columns)]))
        f0 = L.fit_spec(dn, SPECS, "S0")
        f1 = L.fit_spec(dn, SPECS, "Bmu", warm=f0, restart=False)
        br = L.branching(dn, f1)
        nn.append(br.get("n_Bm", 0.0)); nu.append(br.get("n_Bu", 0.0))
    out["null_named_max"] = float(max(nn)); out["null_unnamed_max"] = float(max(nu))
    return out


def main():
    units = L.list_units().filter(pl.col("eligible")).sort("n_calls")
    rows = []
    with Pool(2, maxtasksperchild=4) as pool:
        for r in pool.imap_unordered(run, units["unit_id"].to_list()):
            rows.append(r)
            print(r["unit_id"], f"named={r.get('n_named', 0):.4f} [null {r['null_named_max']:.4f}]",
                  f"unnamed={r.get('n_unnamed', 0):.4f} [null {r['null_unnamed_max']:.4f}]", flush=True)
            pl.DataFrame(rows).write_parquet(L.DATA / "posthoc_mention.parquet")


if __name__ == "__main__":
    main()
