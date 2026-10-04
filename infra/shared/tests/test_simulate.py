"""Tests for infra/shared/simulate.py (DQ8): each dynamics reproduces its planted parameter within tolerance, outputs
match the shared tables' schemas, and real-skeleton extraction respects the holdout.

Fast (toy skeletons, fixed seeds); the real-data tests are skipped when data/processed/shared is absent.
Run: uv run python infra/shared/tests/test_simulate.py      (or: uv run --with pytest pytest infra/shared/tests)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import nulls as NL  # noqa: E402
import simulate as SIM  # noqa: E402

SH = HERE.parents[2] / "data/processed/shared"
HAVE_DATA = (SH / "period_units.parquet").exists() and (SH / "call_windows.parquet").exists()


def _sigmoid(x):
    return 1 / (1 + np.exp(-x))


def _mle_1d(y, off, x, lo=-3.0, hi=5.0):
    """MLE of beta in logit P(y=1) = off + beta x (Newton from 0, bounded)."""
    b = 0.0
    for _ in range(50):
        p = _sigmoid(off + b * x)
        g = ((y - p) * x).sum()
        h = (p * (1 - p) * x * x).sum()
        step = g / max(h, 1e-12)
        b = float(np.clip(b + step, lo, hi))
        if abs(step) < 1e-8:
            break
    return b, 1 / np.sqrt(max(h, 1e-12))


# --------------------------------------------------------------------------------------------- independent
def test_independent_is_rate_matched():
    sk = SIM.toy_skeleton(N=10, n_days=6, T=240, seed=1)
    prof = sk.profiles()
    sim = SIM.simulate(sk, seed=2)
    occ_sim, occ_prof, sw_sim = [], [], []
    for k, (d, ds) in enumerate(zip(sk.days, sim.days)):
        sp = d.span
        occ_sim.append((ds.act & sp).sum(0) / sp.sum(0))
        occ_prof.append((prof["p_act"][k] * sp).sum(0) / sp.sum(0))
        both = sp[1:] & sp[:-1]
        sw_sim.append(((ds.act[1:] != ds.act[:-1]) & both).sum(0) / both.sum(0))
    occ_sim, occ_prof = np.mean(occ_sim, 0), np.mean(occ_prof, 0)
    assert np.max(np.abs(occ_sim - occ_prof)) < 0.05, (occ_sim, occ_prof)
    sw = np.mean(sw_sim, 0)
    assert np.all(np.abs(sw / prof["switch"] - 1) < 0.25), (sw, prof["switch"])
    # talk is a subset of activity and its rate matches the profile
    talk = sum(ds.talk.sum() for ds in sim.days)
    exp_talk = sum((prof["q_talk"][k] * ds.act).sum() for k, ds in enumerate(sim.days))
    assert abs(talk / exp_talk - 1) < 0.1
    assert all(not (ds.talk & ~ds.act).any() for ds in sim.days)


def test_independent_has_no_coupling():
    """On the all-present window (H38's operator rule) independent agents have g ~ 0; on the whole day the staggered
    edges (agents forced silent before their first record, all starting within 15 min) fake a gain."""
    sk = SIM.toy_skeleton(N=12, n_days=6, T=240, seed=3)
    gs, graw = [], []
    for s in range(4):
        sim = SIM.simulate(sk, seed=10 + s)
        days = [np.where(ds.act, 1.0, -1.0) for ds in sim.days]
        valid = [ds.span.all(1) for ds in sim.days]
        gs.append(NL.stat_cw_gain(days, [d.minutes for d in sk.days], valid=valid))
        graw.append(NL.stat_cw_gain(days, [d.minutes for d in sk.days]))
    assert abs(np.mean(gs)) < 0.04, gs
    assert np.mean(graw) > np.mean(gs) + 0.1, (graw, gs)


# --------------------------------------------------------------------------------------------- kinetic Ising
def _pl_coupling(sk, sim, J_scope="village", delay="none"):
    """Pseudo-likelihood MLE of J given the engine's exact offsets (h0 + K s) and the coupling regressor."""
    ys, offs, xs = [], [], []
    for k, (d, ds) in enumerate(zip(sk.days, sim.days)):
        e = SIM.engine_inputs(sk, k)
        S = np.where(ds.act, 1.0, -1.0)
        T, N = S.shape
        RO = SIM._readout_index(sk, d) if delay == "readout" else None
        for t in range(1, T):
            if delay == "none":
                G = np.broadcast_to(S[t - 1] - e["m_exp"][t - 1], (N, N))
            else:
                ix = RO[t]
                G = S[ix] - e["m_exp"][ix]
            M = np.broadcast_to(d.span[t][None, :], (N, N)).copy()
            np.fill_diagonal(M, False)
            c = (G * M).sum(1) / np.maximum(M.sum(1) + 1, 2)
            ok = d.span[t] & d.span[t - 1] & ~ds.stall[t]
            ys.append((S[t, ok] > 0).astype(float))
            offs.append(2 * (e["h0"][t, ok] + e["K"][t, ok] * S[t - 1, ok]))
            xs.append(2 * c[ok])
    return _mle_1d(np.concatenate(ys), np.concatenate(offs), np.concatenate(xs))


def test_kinetic_ising_recovers_J():
    sk = SIM.toy_skeleton(N=12, n_days=6, T=240, seed=4)
    for J in (0.0, 0.8):
        sim = SIM.simulate(sk, seed=5, activity=SIM.ActivityModel(J=J))
        Jh, se = _pl_coupling(sk, sim)
        assert abs(Jh - J) < max(0.15, 3 * se), (J, Jh, se)
    # coupling raises the equal-time gain; g_true is reported
    assert sim.truth["activity"]["g_true"] > 0.1


def test_readout_delay_recovers_J():
    sk = SIM.toy_skeleton(N=10, n_days=6, T=240, call_gap_min=6.0, seed=6)
    sim = SIM.simulate(sk, seed=7, activity=SIM.ActivityModel(J=0.8, delay="readout"))
    Jh, se = _pl_coupling(sk, sim, delay="readout")
    assert abs(Jh - 0.8) < max(0.2, 3 * se), (Jh, se)
    Jn, _ = _pl_coupling(sk, sim, delay="none")   # the misspecified (no-delay) regressor attenuates J
    assert Jn < Jh
    assert sim.truth["activity"]["readout_lag_median_min"] >= 1


# --------------------------------------------------------------------------------------------- fields, edges, stalls
def test_shared_field_without_coupling_raises_gain():
    sk = SIM.toy_skeleton(N=12, n_days=5, T=240, seed=8)
    g0 = NL.stat_cw_gain([np.where(ds.act, 1.0, -1.0) for ds in SIM.simulate(sk, seed=9).days],
                         [d.minutes for d in sk.days])
    simf = SIM.simulate(sk, seed=9, **SIM.preset("global_field", global_sd=0.8, global_tau=10))
    gf = NL.stat_cw_gain([np.where(ds.act, 1.0, -1.0) for ds in simf.days], [d.minutes for d in sk.days])
    assert simf.truth["activity"]["J"] == 0 and gf > g0 + 0.1, (g0, gf)


def test_day_edge_synchronizes_spans():
    sk = SIM.toy_skeleton(N=10, n_days=3, T=240, edge_jitter=20, seed=10)
    sim = SIM.simulate(sk, seed=11, edge=SIM.EdgeDrive(jitter=2))
    for ds in sim.days:
        first = ds.span.argmax(0)
        last = ds.span.shape[0] - 1 - ds.span[::-1].argmax(0)
        assert first.max() - first.min() <= 2 and last.max() - last.min() <= 2
    real_first = sk.days[0].span.argmax(0)
    assert real_first.max() - real_first.min() > 2


def test_planted_stalls():
    sk = SIM.toy_skeleton(N=10, n_days=30, T=240, seed=12)
    sim = SIM.simulate(sk, seed=13, stalls=SIM.StallModel(pi=0.10, free_prob=0.0, marked_prob=1.0, reason_prob=1.0))
    sess = np.concatenate([ds.span.any(1) for ds in sim.days])
    st = np.concatenate([ds.stall for ds in sim.days])
    assert abs(st[sess].mean() - 0.10) < 0.03, st[sess].mean()
    for ds in sim.days:
        assert not ds.act[ds.stall].any()                                  # everyone silent (no free agent)
        assert ((ds.reasons == SIM.R_INFRA) & ds.span)[ds.stall].mean() > 0.5  # marked with infra reasons
    tab = sim.tables()["stall_minutes"]
    assert tab.filter(tab["planted_stall"])["K"].max() == 0


# --------------------------------------------------------------------------------------------- Hawkes
def _em_branching(times, base_rate, tau, t0, t1, iters=60):
    """EM for a univariate Hawkes with exponential kernel (known tau) and baseline c * base_rate(t) (piecewise
    per minute, events/min). Returns the branching ratio n."""
    t = np.sort(times)
    m = np.clip(((t - t0) // 60).astype(int), 0, len(base_rate) - 1)
    B = base_rate[m] / 60.0                   # per second, shape known
    Bint = base_rate.sum()                    # integral of base_rate over the window (events)
    c, n = 0.5, 0.3
    K = 30
    for _ in range(iters):
        lam_b = c * B
        P = np.zeros((len(t), K))
        for k in range(1, K + 1):
            dtk = np.r_[np.full(k, np.inf), t[k:] - t[:-k]]
            P[:, k - 1] = n * np.exp(-dtk / tau) / tau
        tot = lam_b + P.sum(1)
        c = (lam_b / tot).sum() / Bint
        n = (P.sum(1) / tot).sum() / len(t)
    return n


def test_hawkes_branching_and_rates():
    sk = SIM.toy_skeleton(N=10, n_days=4, T=240, talk_frac=0.25, seed=14)
    prof = sk.profiles()
    n_x, n_s, tau = 0.35, 0.15, 90.0
    sim = SIM.simulate(sk, seed=15, talk=SIM.TalkModel(kind="hawkes", n_x=n_x, n_s=n_s, tau_s=tau))
    br = sim.truth["talk"]["branching_realized"]
    assert abs(br - (n_x + n_s)) < 0.07, br
    real = sum(float(prof["r_msg"][k].sum()) for k in range(len(sk.days)))
    simn = sum(len(ds.msgs["t_s"]) for ds in sim.days)
    assert abs(simn / real - 1) < 0.15, (simn, real)
    ests = []
    for k, (d, ds) in enumerate(zip(sk.days, sim.days)):
        base = np.where(d.span, prof["r_msg"][k], 0).sum(1)
        ests.append(_em_branching(ds.msgs["t_s"], base, tau, d.minute0 * 60.0, (d.minute0 + d.T) * 60.0))
    assert abs(np.mean(ests) - (n_x + n_s)) < 0.12, ests
    # children mention their parent's author at the configured rate
    ds = sim.days[0]
    ch = ds.msgs["parent"] >= 0
    hit = (ds.msgs["mention"][ch] == ds.msgs["agent"][ds.msgs["parent"][ch]]).mean()
    assert 0.3 < hit < 0.7


# --------------------------------------------------------------------------------------------- content
def _window_presence(sk, sim):
    out = []
    for d, ds in zip(sk.days, sim.days):
        out.append(np.stack([ds.span[w * 30:(w + 1) * 30].any(0) & d.on_roster for w in range(d.W)]))
    return out


def test_vector_spin_recovers_J():
    sk = SIM.toy_skeleton(N=12, n_days=5, T=240, n_rooms=2, seed=16)
    J, phi = 0.6, 0.6
    sim = SIM.simulate(sk, seed=17, content=SIM.ContentModel(kind="ou", J=J, phi=phi, scope="room"))
    Z = np.concatenate([ds.z for ds in sim.days], 0)             # (W_total, N, d)
    pres = np.concatenate(_window_presence(sk, sim), 0)
    rooms = np.concatenate([d.room[np.minimum(np.arange(d.W) * 30 + 15, d.T - 1)] for d in sk.days], 0)
    num = den = 0.0
    for w in range(1, len(Z)):
        same = (rooms[w][:, None] == rooms[w][None, :]) & pres[w][None, :]
        np.fill_diagonal(same, False)
        m = same.astype(float) @ Z[w - 1] / np.maximum(same.sum(1), 1)[:, None]
        x = (1 - phi) * m
        y = Z[w] - phi * Z[w - 1]
        num += (x * y).sum()
        den += (x * x).sum()
    Jh = num / den
    assert abs(Jh - J) < 0.15, Jh
    g = sim.truth["content"]["g_true"]
    assert 0 < g < J
    # statements: real counts reproduced, unit float16 32-d vectors in the table
    tabs = sim.tables()
    n_real = int(sum(np.where(d.on_roster, d.stmt_count, 0).sum() for d in sk.days))
    assert tabs["statements"].height == n_real
    V = sim.statement_vectors
    assert V.shape == (n_real, 32) and V.dtype == np.float16
    assert np.allclose(np.linalg.norm(V.astype(np.float32), axis=1), 1, atol=2e-3)


def test_degroot_recovers_alpha():
    sk = SIM.toy_skeleton(N=10, n_days=4, T=240, stmt_rate=3.0, seed=18)
    alpha = 0.4
    cm = SIM.ContentModel(kind="degroot", alpha=alpha, innov=0.05, scope="village")
    sim = SIM.simulate(sk, seed=19, content=cm)
    st, goal = sim.truth["content"]["static"], sim.truth["content"]["goal_dir"]
    num = den = 0.0
    zprev = None
    for d, ds in zip(sk.days, sim.days):
        s = ds.stmts
        for w in range(d.W):
            z = ds.z[w]
            if zprev is not None and w > 0:
                sel = s["win"] == w - 1
                act_w = ds.act[w * 30:(w + 1) * 30].any(0)
                for i in np.flatnonzero(act_w):
                    o = sel & (s["agent"] != i)
                    if not o.any():
                        continue
                    tgt = s["vec"][o].mean(0) - (st[i] + 0.6 * goal)
                    x = tgt - zprev[i]
                    num += x @ (z[i] - zprev[i])
                    den += x @ x
            zprev = z
    ah = num / den
    assert abs(ah - alpha) < 0.1, ah


# --------------------------------------------------------------------------------------------- Potts
def test_potts_recovers_J():
    from scipy.optimize import minimize
    sk = SIM.toy_skeleton(N=12, n_days=12, T=240, seed=20)
    q, J = 4, 2.0
    sim = SIM.simulate(sk, seed=21, projects=SIM.ProjectModel(q=q, J=J, p_reconsider=0.4, waves_per_day=0.5))
    waves = {(k, w) for (k, w, a, n) in sim.truth["projects"]["waves"]}
    L = np.concatenate([ds.labels for ds in sim.days], 0)
    key = [(k, w) for k, d in enumerate(sk.days) for w in range(d.W)]
    rows = []
    for t in range(1, len(L)):
        if key[t] in waves:
            continue
        prev, cur = L[t - 1], L[t]
        for i in range(sk.N):
            oth = np.delete(prev, i)
            frac = np.bincount(oth, minlength=q + 1)[1:q + 1] / len(oth)
            rows.append((prev[i] - 1, cur[i] - 1, frac))
    pi = np.array([r[0] for r in rows])
    ci = np.array([r[1] for r in rows])
    F = np.stack([r[2] for r in rows])

    def nll(th):
        p = 1 / (1 + np.exp(-th[0]))
        lg = th[1] * F
        sm = np.exp(lg - lg.max(1, keepdims=True))
        sm /= sm.sum(1, keepdims=True)
        lik = (1 - p) * (ci == pi) + p * sm[np.arange(len(ci)), ci]
        return -np.log(np.maximum(lik, 1e-300)).sum()
    r = minimize(nll, np.array([0.0, 0.0]), method="Nelder-Mead")
    p_hat, J_hat = 1 / (1 + np.exp(-r.x[0])), r.x[1]
    assert abs(p_hat - 0.4) < 0.08 and abs(J_hat - J) < 0.6, (p_hat, J_hat)
    tab = sim.tables()["project_states"]
    assert tab.height == int(sum(((ds.labels >= 0) & d.label_mask).sum() for d, ds in zip(sk.days, sim.days)))


# --------------------------------------------------------------------------------------------- kicks
def test_kick_field_response():
    sk = SIM.toy_skeleton(N=10, n_days=6, T=240, nudge_rate=0, mention_rate=0, seed=22)
    effs = {}
    for h in (0.0, 1.5):
        km = SIM.KickModel(effects={"nudge": (h, 2, 20)}, source="idle", rate=0.04)
        sim = SIM.simulate(sk, seed=23, kicks=km)
        di = {d.pt_date: k for k, d in enumerate(sk.days)}
        kicks = [[] for _ in sk.days]
        for (pt, m, i, kind, hh, dl, du) in sim.kick_truth:
            kicks[di[pt]].append((m, i))
        r = NL.lever_design(kicks, [ds.act for ds in sim.days], W=20, present=[ds.span for ds in sim.days],
                            rng=np.random.default_rng(1))
        effs[h] = float(np.mean(r["y_ep"] - r["y_ctrl"]))
        assert r["n_ep"] > 50
    assert abs(effs[0.0]) < 0.05 and effs[1.5] > 0.1, effs


# --------------------------------------------------------------------------------------------- tables
def test_tables_match_shared_schemas():
    sk = SIM.toy_skeleton(N=8, n_days=2, T=120, seed=24)
    sim = SIM.simulate(sk, seed=25, content=SIM.ContentModel(), projects=SIM.ProjectModel())
    tabs = sim.tables()
    expected = {
        "activity_bins": ["pt_date", "minute", "active_min", "agent", "talk", "idle", "consolidate", "other_event",
                          "turns", "paused", "state"],
        "chat_core": ["message_id", "t", "pt_date", "goal_no", "regime", "room", "speaker_kind", "agent", "human",
                      "length", "mentions", "n_urls"],
        "statements": ["kind", "src_row", "agent", "t", "pt_date", "room", "goal_no", "regime", "holdout", "win30"],
        "project_states": ["w_min", "sources", "goal_no", "pt_date", "day", "win", "agent", "room", "project", "n",
                           "n_all", "n_tied", "label", "holdout"],
        "kicks_classified": ["t", "kind", "subkind", "targeted", "room", "speaker", "targets", "n_targets",
                             "recipients", "msg", "message_id", "goal_no", "pt_date", "ref", "holdout"],
    }
    for name, cols in expected.items():
        assert tabs[name].columns == cols, (name, tabs[name].columns)
    if HAVE_DATA:
        import polars as pl
        for name, real in (("activity_bins", "activity_bins"), ("chat_core", "chat_core"),
                           ("statements", "embeddings/statements"), ("project_states", "project_states"),
                           ("kicks_classified", "kicks_classified")):
            rs = pl.scan_parquet(SH / f"{real}.parquet").collect_schema()
            ss = tabs[name].schema
            for c in expected[name]:
                assert ss[c] == rs[c], (name, c, ss[c], rs[c])
    # no text anywhere: every String column is an id, date, kind or synthetic label
    for name, df in tabs.items():
        for c, dt_ in df.schema.items():
            if str(dt_) == "String" and df[c].drop_nulls().len():
                assert df[c].drop_nulls().str.len_chars().max() <= 40, (name, c)


def test_presets_all_run():
    sk = SIM.toy_skeleton(N=6, n_days=2, T=90, seed=26)
    for name in SIM.DYNAMICS:
        sim = SIM.simulate(sk, seed=1, **SIM.preset(name))
        assert sim.tables()["activity_bins"].height == 6 * 90 * 2


# --------------------------------------------------------------------------------------------- real skeletons
def test_real_skeleton_and_holdout():
    if not HAVE_DATA:
        print("skip: no shared data")
        return
    sk = SIM.extract_skeleton("41")
    s = sk.summary()
    assert s["N"] >= 10 and s["n_days"] == 5 and s["n_calls"] > 1000 and s["n_stmts"] > 500
    sim = SIM.simulate(sk, seed=3)
    real_act = sum(int((d.state >= 3).sum()) for d in sk.days)
    sim_act = sum(int(ds.act.sum()) for ds in sim.days)
    assert abs(sim_act / real_act - 1) < 0.05, (sim_act, real_act)
    import polars as pl
    held = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("holdout"))["unit_id"][0]
    try:
        SIM.extract_skeleton(held)
        raise AssertionError("holdout unit extracted without allow_holdout")
    except SIM.HoldoutError:
        pass


if __name__ == "__main__":
    import time
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            t0 = time.time()
            try:
                fn()
                print(f"PASS {name} ({time.time() - t0:.1f}s)")
            except Exception as e:  # noqa: BLE001
                fails += 1
                print(f"FAIL {name}: {type(e).__name__}: {e}")
    sys.exit(1 if fails else 0)
