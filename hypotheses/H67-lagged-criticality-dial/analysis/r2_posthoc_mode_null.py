"""H67 round 2, post hoc P2 null check: the mode-free gain (cells agent x day x wake) and the mode outcome on synthetic
worlds built on the real regime-I call skeletons (call modes and times fixed; talk and messages simulated).
    uv run python hypotheses/H67-lagged-criticality-dial/analysis/r2_posthoc_mode_null.py
"""
import numpy as np, polars as pl, h67lib as L, r2_synthetic as S
from concurrent.futures import ProcessPoolExecutor
def job(a):
    u, world, g, rep = a
    c, m0 = S.load(u); rb = S.design_rbar(c, m0)
    rng = np.random.default_rng(S.seed_of('nm', u, world, rep))
    sim, m = L.simulate(c, g, rb, rng, burst=(world == 'burst'))
    d = L.all_counts(sim, m).with_columns(pl.col('is_wake').cast(pl.Int8).alias('cls'))
    r = L.fit(d, m, 'main', True, B=0)
    dm = d.with_columns(pl.col('is_chat').cast(pl.Boolean).alias('talk'))
    rm = L.fit(dm, m, 'main', True, B=0)
    return (u, world, rep, r.get('g'), rm.get('J1'), g / rb * r['rbar'] * r['mbar'])
def main():
    import sys
    if '--all' in sys.argv:
        ids = pl.read_parquet(L.OUT / 'results' / 'units.parquet').filter(pl.col('ok') & (pl.col('regime') == 'I'))['unit_id'].to_list()
        jobs = [(u, 'null', 0.0, k) for u in ids for k in range(8)]
        with ProcessPoolExecutor(2) as ex:
            res = list(ex.map(job, jobs))
        df = pl.DataFrame(res, schema=['u', 'world', 'rep', 'g_nomode', 'J_mode', 'g_true'], orient='row')
        df.write_parquet(L.OUT / 'round2' / 'synthetic' / 'posthoc_mode_null_all.parquet')
        print(df.group_by('u').agg(pl.col('g_nomode').median(), pl.col('J_mode').median()).sort('u'))
        return
    jobs = [(u, w, g, k) for u in ['4c', '19a', '27'] for (w, g) in [('null', 0.0), ('burst', 0.0), ('g015', 0.15)] for k in range(8)]
    with ProcessPoolExecutor(2) as ex:
        res = list(ex.map(job, jobs))
    df = pl.DataFrame(res, schema=['u', 'world', 'rep', 'g_nomode', 'J_mode', 'g_true'], orient='row')
    print(df.group_by('world', 'u').agg(pl.col('g_nomode').median(), pl.col('J_mode').median(), pl.col('g_true').median()).sort('world', 'u'))
    print(df.group_by('world').agg(pl.col('g_nomode').median(), pl.col('J_mode').median(), pl.col('g_true').median()))
    df.write_parquet(L.OUT / 'round2' / 'synthetic' / 'posthoc_mode_null.parquet')

if __name__ == "__main__":
    main()
