"""H09 round 2, E6: idle traps done properly (T5, HH53). NON-HOLDOUT days only.

Definitions (as pre-registered on the card, Round 2 block):
  idle spell  = maximal run of one agent's consecutive idle events (WAIT / PAUSE) with no non-idle
                action in between. Non-idle action = any other events_core agent event, or any
                computer-use turn in `actions` except the `pause` tool call itself (which mirrors the
                PAUSE event ~0.1 s later). The spell ends at the next non-idle action on the same PT
                day; otherwise it is right-censored at the day's window end.
  per-PAUSE   = (regime III) time from a PAUSE event to the agent's next row of any kind (next turn),
                compared with the declared duration pause_s.
  kicks       = chat messages by others in the agent's room (`exposure`), split by speaker kind and
                by whether the message @-mentions the agent.
Hazard: discrete time, 10-s bins at risk; a bin is "kicked" if a kick arrived in the TAU seconds before
the bin starts. Mantel-Haenszel rate ratio over strata (elapsed dwell x hour of day).
Null: each agent-day's kick timeline replaced by the same agent's timeline on another random
non-holdout day of the same regime, at the same clock offset from the window start.

Usage: uv run python hypotheses/H09-swarm-thermodynamics/analysis/explore_e6_idle_traps.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
from scipy import optimize, special, stats

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
OUTD = ROOT / "data/processed/H09-swarm-thermodynamics"
FIG = Path(__file__).resolve().parents[1] / "figures"
OUTD.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20261003)
plt.rcParams.update({"font.family": "serif", "font.size": 7, "axes.linewidth": 0.5, "pdf.fonttype": 42})
BIN = 10            # s, hazard resolution
TAUS = (30, 60, 120)
TAU = 60            # primary look-back window for "kicked"
N_NULL = 100
EL_EDGES = np.array([0, 30, 60, 120, 300, 600, 1200, 3600, 1e9])
R = {}

cal = pl.read_parquet(SH / "calendar.parquet")
keep = cal.filter(~pl.col("holdout")).select("pt_date", pl.col("regime").cast(pl.Utf8).alias("reg"), "win_start", "win_end")
roster = pl.read_parquet(SH / "roster.parquet")
labs = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
R["days_used"] = {r: int(n) for r, n in keep.group_by("reg").len().iter_rows()}

# ------------------------------------------------------------------ timeline: idle events + awake turns
ev = (pl.read_parquet(SH / "events_core.parquet", columns=["t", "pt_date", "actor_kind", "agent", "action_type", "pause_s"])
      .filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null())
      .join(keep.select("pt_date"), on="pt_date")
      .select("agent", "t", "pt_date", pl.col("action_type").cast(pl.Utf8).alias("kind"), "pause_s"))
acts_all = (pl.read_parquet(SH / "actions.parquet", columns=["t", "agent", "action"])
            .filter(pl.col("agent").is_not_null())
            .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
            .join(keep.select("pt_date"), on="pt_date")
            .select("agent", "t", "pt_date", pl.col("action").cast(pl.Utf8).alias("action")))


def make_spells(exclude_actions):
    acts = (acts_all.filter(~pl.col("action").is_in(list(exclude_actions)))
            .select("agent", "t", "pt_date", (pl.lit("turn:") + pl.col("action")).alias("kind"),
                    pl.lit(None, dtype=pl.Float32).alias("pause_s")))
    tl = (pl.concat([ev, acts]).with_columns(pl.col("kind").is_in(["WAIT", "PAUSE"]).alias("idle"))
          .join(keep, on="pt_date")
          .sort("agent", "t"))
    tl = tl.with_columns(pl.col("t").shift(-1).over("agent", "pt_date").alias("t_next_row"))
    tl = tl.with_columns((pl.col("idle") != pl.col("idle").shift(1).over("agent", "pt_date")).fill_null(True)
                         .cum_sum().over("agent", "pt_date").alias("run"))
    runs = (tl.group_by("agent", "pt_date", "run")
            .agg(pl.col("idle").first(), pl.col("t").first().alias("t0"), pl.len().alias("n_events"),
                 pl.col("kind").first().alias("kind0"), pl.col("pause_s").first().alias("decl0"),
                 pl.col("reg").first(), pl.col("win_start").first(), pl.col("win_end").first())
            .sort("agent", "pt_date", "run")
            .with_columns(pl.col("t0").shift(-1).over("agent", "pt_date").alias("t_end")))
    sp = (runs.filter(pl.col("idle"))
          .with_columns(pl.col("t_end").is_null().alias("cens"),
                        pl.coalesce("t_end", "win_end").alias("t1"))
          .with_columns(((pl.col("t1") - pl.col("t0")).dt.total_seconds()).alias("dwell"),
                        ((pl.col("t0") - pl.col("win_start")).dt.total_seconds()).alias("off0"))
          .filter(pl.col("dwell") >= 0)
          .with_columns(pl.col("agent").replace_strict(labs, default="?").alias("lab")))
    return tl, sp.filter(pl.col("reg").is_in(["I", "III"]))


tl, _sp_event = make_spells({"pause"})
# Spells for analysis come from the reusable table (build_observables.py). Regime I: WAIT is logged < 1 s
# before the next action in ~82% of runs, so the idle interval is the GAP from the previous non-idle row to
# the next one (gap_dwell_s). Regime III: from the PAUSE to the next non-idle row (dwell_s).
IR = (pl.read_parquet(OUTD / "idle_runs.parquet").filter(~pl.col("holdout") & pl.col("regime").is_in(["I", "III"]))
      .join(keep.select("pt_date", "win_start"), on="pt_date"))
sp = (IR.with_columns(pl.when(pl.col("regime") == "I").then(pl.col("t_prev_action")).otherwise(pl.col("t_start")).alias("t0"))
      .filter(pl.col("t0").is_not_null())
      .with_columns(pl.when(pl.col("regime") == "I").then(pl.col("gap_dwell_s")).otherwise(pl.col("dwell_s")).cast(pl.Float64).alias("dwell"),
                    ((pl.col("t0") - pl.col("win_start")).dt.total_milliseconds() / 1000).alias("off0"),
                    pl.col("censored").alias("cens"), pl.col("regime").alias("reg"), pl.col("idle_kind").alias("kind0"),
                    pl.col("agent").replace_strict(labs, default="?").alias("lab"))
      .select("agent", "pt_date", "reg", "t0", "dwell", "cens", "off0", "kind0", "lab"))
R["regimeI_wait_logged_lt1s_before_next_action"] = float(IR.filter((pl.col("regime") == "I") & (pl.col("idle_kind") == "WAIT"))
                                                          .select((pl.col("dwell_s") < 1).mean()).item())
# baseline for regime I: gaps between consecutive non-idle agent EVENTS with and without a WAIT in between
_e = (ev.join(keep.filter(pl.col("reg") == "I").select("pt_date"), on="pt_date").sort("agent", "t")
      .with_columns(pl.col("kind").is_in(["WAIT", "PAUSE"]).alias("idle")))
_e = _e.with_columns(pl.col("idle").cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("ci"))
_n = (_e.filter(~pl.col("idle")).with_columns(
    ((pl.col("t") - pl.col("t").shift(1).over("agent", "pt_date")).dt.total_milliseconds() / 1000).alias("gap"),
    (pl.col("ci") - pl.col("ci").shift(1).over("agent", "pt_date")).alias("n_wait_between")).drop_nulls("gap"))
R["regimeI_gap_baseline"] = {
    "median_gap_no_wait_s": float(_n.filter(pl.col("n_wait_between") == 0)["gap"].median()),
    "median_gap_with_wait_s": float(_n.filter(pl.col("n_wait_between") > 0)["gap"].median()),
    "p90_gap_no_wait_s": float(_n.filter(pl.col("n_wait_between") == 0)["gap"].quantile(0.9)),
    "p90_gap_with_wait_s": float(_n.filter(pl.col("n_wait_between") > 0)["gap"].quantile(0.9)),
    "n_no_wait": int((_n["n_wait_between"] == 0).sum()), "n_with_wait": int((_n["n_wait_between"] > 0).sum())}
R["spells"] = {r: {"n": int(g.height), "censored_frac": float(g["cens"].mean()),
                   "kinds": dict(g.group_by("kind0").len().iter_rows())}
               for (r,), g in sp.group_by("reg")}
R["regime_II_note"] = "regime II has 9 non-holdout days; excluded from E6 (counts only)"

# ------------------------------------------------------------------ E6a: tail shape (censored MLE above x_min)


def tail_fits(x, c, xmin):
    m = x > xmin
    x, c = x[m], c[m]
    u = ~c
    lx = np.log(x)
    out = {"n_tail": int(len(x)), "n_censored": int(c.sum()), "xmin_s": float(xmin)}

    def nll_exp(p):
        lam = np.exp(p[0])
        return -(np.sum(np.log(lam) - lam * (x[u] - xmin)) + np.sum(-lam * (x[c] - xmin)))

    def nll_pl(p):
        a = 1 + np.exp(p[0])  # pdf (a-1)/xmin (x/xmin)^-a
        return -(np.sum(np.log(a - 1) - np.log(xmin) - a * np.log(x[u] / xmin)) + np.sum(-(a - 1) * np.log(x[c] / xmin)))

    def nll_ln(p):
        mu, s = p[0], np.exp(p[1])
        z0 = (np.log(xmin) - mu) / s
        lS0 = special.log_ndtr(-z0)
        zu = (lx[u] - mu) / s; zc = (lx[c] - mu) / s
        return -(np.sum(-lx[u] - np.log(s) - 0.5 * np.log(2 * np.pi) - 0.5 * zu ** 2 - lS0) + np.sum(special.log_ndtr(-zc) - lS0))

    def nll_wb(p):
        k, lam = np.exp(p[0]), np.exp(p[1])  # S(x)=exp(-(x/lam)^k)
        H = lambda y: (y / lam) ** k
        return -(np.sum(np.log(k / lam) + (k - 1) * np.log(x[u] / lam) - H(x[u]) + H(xmin)) + np.sum(-H(x[c]) + H(xmin)))

    starts = {"exponential": [np.log(1 / max(np.mean(x - xmin), 1e-6))], "power_law": [np.log(1.0)],
              "lognormal": [np.mean(lx), np.log(np.std(lx) + 1e-6)], "stretched_exp": [np.log(0.5), np.log(np.median(x))]}
    fns = {"exponential": nll_exp, "power_law": nll_pl, "lognormal": nll_ln, "stretched_exp": nll_wb}
    for k, f in fns.items():
        best = None
        for jitter in (0, 0.5, -0.5):
            r = optimize.minimize(f, np.array(starts[k]) + jitter, method="Nelder-Mead", options={"maxiter": 4000, "xatol": 1e-6, "fatol": 1e-6})
            if best is None or r.fun < best.fun:
                best = r
        p = best.x
        par = {"exponential": lambda p: {"rate_per_s": float(np.exp(p[0]))},
               "power_law": lambda p: {"alpha": float(1 + np.exp(p[0]))},
               "lognormal": lambda p: {"mu": float(p[0]), "sigma": float(np.exp(p[1]))},
               "stretched_exp": lambda p: {"beta": float(np.exp(p[0])), "scale_s": float(np.exp(p[1]))}}[k](p)
        out[k] = {"nll": float(best.fun), "aic": float(2 * best.fun + 2 * len(p)), **par}
    a = {k: out[k]["aic"] for k in fns}
    best = min(a, key=a.get)
    out["best_by_aic"] = best
    out["delta_aic_vs_best"] = {k: float(v - a[best]) for k, v in a.items()}
    return out


e6a = {}
for reg in ("I", "III"):
    g = sp.filter(pl.col("reg") == reg)
    x, c = g["dwell"].to_numpy().astype(float), g["cens"].to_numpy()
    xu = x[~c]
    pos = x[x > 0]
    xmin = float(np.median(pos))
    e6a[reg] = {"n": int(len(x)), "frac_zero_dwell": float(np.mean(x <= 0)), "median_s": float(np.median(x)),
                "mean_uncens_s": float(xu.mean()), "cv_uncens": float(xu.std() / xu.mean()),
                "p90_s": float(np.percentile(x, 90)), "p99_s": float(np.percentile(x, 99)),
                "fits_above_median": tail_fits(np.maximum(x, 1e-3), c, xmin),
                "fits_above_p90": tail_fits(np.maximum(x, 1e-3), c, float(np.percentile(pos, 90)))}
R["E6a_tail"] = e6a

# ------------------------------------------------------------------ E6b: declared vs realized pauses (regime III)
pz = (tl.filter((pl.col("kind") == "PAUSE") & (pl.col("reg") == "III"))
      .with_columns(((pl.col("t_next_row") - pl.col("t")).dt.total_seconds()).alias("realized"),
                    pl.col("t_next_row").is_null().alias("cens")))
decl = pz["pause_s"].to_numpy().astype(float)
real = pz["realized"].to_numpy()
cens = pz["cens"].to_numpy()
ok = ~cens
early = ok & (real < decl - 30)
late_lat = (real - decl)[ok & ~early]
vals, cnts = np.unique(decl, return_counts=True)
top = sorted(zip(cnts, vals), reverse=True)[:10]
R["E6b_pauses"] = {
    "n_pause": int(len(decl)), "censored_frac": float(cens.mean()),
    "frac_whole_minutes": float(np.mean(np.isclose(np.mod(decl, 60), 0))),
    "frac_12h_default": float(np.mean(decl == 43200)),
    "top_declared_s": [[float(v), int(n)] for n, v in top],
    "declared_median_s": float(np.median(decl)),
    "frac_early_gt30s": float(early.sum() / ok.sum()),
    "frac_early_excl_12h": float((early & (decl < 43200)).sum() / (ok & (decl < 43200)).sum()),
    "wake_latency_after_expiry_median_s": float(np.median(late_lat)) if len(late_lat) else None,
    "realized_over_declared_median": float(np.median(real[ok] / np.maximum(decl[ok], 1))),
}

# ------------------------------------------------------------------ kicks per agent
chat = pl.read_parquet(SH / "chat_core.parquet", columns=["t", "pt_date", "speaker_kind", "mentions"]).with_row_index("msg")
ex = pl.read_parquet(SH / "exposure.parquet", columns=["msg", "agent"])
k = (ex.join(chat, on="msg").join(keep.select("pt_date", "reg", "win_start"), on="pt_date")
     .with_columns(pl.col("mentions").list.contains(pl.col("agent")).fill_null(False).alias("mention"),
                   pl.col("speaker_kind").cast(pl.Utf8).alias("sk"),
                   ((pl.col("t") - pl.col("win_start")).dt.total_seconds()).alias("off"))
     .select("agent", "pt_date", "reg", "off", "sk", "mention"))
KTYPES = {"any": pl.lit(True), "agent_msg": pl.col("sk") == "agent", "human_msg": pl.col("sk") == "human",
          "nudger_msg": pl.col("sk") == "automated", "mention": pl.col("mention"),
          "unmentioned": ~pl.col("mention")}

# agent-day ids per regime; global key arrays for vectorized searchsorted
SHIFT = 200_000.0  # s, offsets are in (-SHIFT, SHIFT)
BIG = 1_000_000.0


def build(reg, sp_reg):
    ad = (pl.concat([sp_reg.select("agent", "pt_date"), k.filter(pl.col("reg") == reg).select("agent", "pt_date")])
          .unique().sort("agent", "pt_date").with_row_index("ad"))
    kk = k.filter(pl.col("reg") == reg).join(ad, on=["agent", "pt_date"])
    keys = {}
    for name, cond in KTYPES.items():
        q = kk.filter(cond)
        keys[name] = np.sort(q["ad"].to_numpy().astype(np.float64) * BIG + q["off"].to_numpy() + SHIFT)
    # spell bins
    s = sp_reg.join(ad, on=["agent", "pt_date"]).with_columns(pl.col("dwell").cast(pl.Float64))
    d = s["dwell"].to_numpy(); c = s["cens"].to_numpy()
    nb = np.where(c, np.floor(d / BIN), np.floor(d / BIN) + 1).astype(np.int64)
    sid = np.repeat(np.arange(len(d)), nb)
    b = np.arange(nb.sum()) - np.repeat(np.cumsum(nb) - nb, nb)
    event = np.zeros(len(b), bool)
    last = np.cumsum(nb) - 1
    event[last[(~c) & (nb > 0)]] = True
    off0 = s["off0"].to_numpy()
    boff = off0[sid] + b * BIN                     # clock offset of bin start
    el = b * BIN
    hour = np.clip(boff // 3600, 0, 9).astype(int)
    stratum = np.searchsorted(EL_EDGES, el, side="right") * 10 + hour
    adid = s["ad"].to_numpy()[sid].astype(np.float64)
    # day-swap map: for each agent-day, candidate other days of the same agent & regime
    adf = ad.to_pandas() if False else ad
    by_agent = {}
    for a_, d_, i_ in adf.select("agent", "pt_date", "ad").iter_rows():
        by_agent.setdefault(a_, []).append(i_)
    return dict(s=s, sid=sid, b=b, event=event, boff=boff, stratum=stratum, adid=adid, keys=keys,
                ad=ad, by_agent=by_agent, nspell=len(d))


def kicked(keys_arr, adid, boff, tau):
    lo = adid * BIG + boff - tau + SHIFT
    hi = adid * BIG + boff + SHIFT
    return np.searchsorted(keys_arr, hi, side="left") - np.searchsorted(keys_arr, lo, side="left") > 0


def mh_rr(event, kick, stratum):
    # MH incidence rate ratio; each bin = BIN seconds at risk
    S = stratum
    T1 = np.bincount(S, weights=kick); T0 = np.bincount(S, weights=~kick)
    d1 = np.bincount(S, weights=event & kick); d0 = np.bincount(S, weights=event & ~kick)
    T = T1 + T0
    m = T > 0
    num = np.sum(d1[m] * T0[m] / T[m]); den = np.sum(d0[m] * T1[m] / T[m])
    crude1 = d1.sum() / max(T1.sum(), 1); crude0 = d0.sum() / max(T0.sum(), 1)
    return float(num / den) if den > 0 else float("nan"), float(crude1 / crude0) if crude0 > 0 else float("nan"), float(T1.sum() / T.sum())


def swap_map(B, rng):
    """Map each agent-day id -> another agent-day id of the same agent (different day)."""
    n = B["ad"].height
    mp = np.arange(n, dtype=np.float64)
    for a_, ids in B["by_agent"].items():
        ids = np.array(ids)
        if len(ids) < 2:
            continue
        perm = rng.permutation(len(ids))
        # derangement-ish: shift by a random non-zero amount in a random order
        shift = rng.integers(1, len(ids))
        tgt = ids[perm][(np.arange(len(ids)) + shift) % len(ids)]
        mp[ids[perm]] = tgt
    return mp


e6c = {}
haz_store = {}
for reg in ("I", "III"):
    B = build(reg, sp.filter(pl.col("reg") == reg))
    out = {"n_bins": int(len(B["b"])), "n_escapes": int(B["event"].sum())}
    for name in KTYPES:
        res = {}
        for tau in TAUS:
            kk_ = kicked(B["keys"][name], B["adid"], B["boff"], tau)
            rr, crude, share = mh_rr(B["event"], kk_, B["stratum"])
            res[f"tau{tau}"] = {"rr_mh": rr, "rr_crude": crude, "frac_bins_kicked": share}
        out[name] = res
    # null for the primary (any, mention, nudger) at TAU
    nulls = {n: [] for n in ("any", "mention", "nudger_msg", "human_msg", "agent_msg")}
    for it in range(N_NULL):
        mp = swap_map(B, RNG)
        adn = mp[B["adid"].astype(np.int64)]
        for n in nulls:
            kk_ = kicked(B["keys"][n], adn, B["boff"], TAU)
            nulls[n].append(mh_rr(B["event"], kk_, B["stratum"])[0])
    for n, v in nulls.items():
        v = np.array(v)
        obs = out[n][f"tau{TAU}"]["rr_mh"]
        out[n]["null_dayswap_tau60"] = {"median": float(np.nanmedian(v)), "p95": float(np.nanpercentile(v, 95)),
                                        "p_ge_obs": float((np.sum(v >= obs) + 1) / (np.sum(~np.isnan(v)) + 1))}
    # block bootstrap CI over agent-days for 'any' and 'mention'
    for n in ("any", "mention"):
        kk_ = kicked(B["keys"][n], B["adid"], B["boff"], TAU)
        ad_i = B["adid"].astype(np.int64)
        nad = B["ad"].height
        S = B["stratum"]; ns = S.max() + 1
        key = ad_i * ns + S
        M = nad * ns
        T1 = np.bincount(key, weights=kk_, minlength=M).reshape(nad, ns); T0 = np.bincount(key, weights=~kk_, minlength=M).reshape(nad, ns)
        d1 = np.bincount(key, weights=B["event"] & kk_, minlength=M).reshape(nad, ns); d0 = np.bincount(key, weights=B["event"] & ~kk_, minlength=M).reshape(nad, ns)
        bs = []
        for _ in range(300):
            w = np.bincount(RNG.integers(0, nad, nad), minlength=nad)[:, None]
            t1, t0, e1, e0 = (T1 * w).sum(0), (T0 * w).sum(0), (d1 * w).sum(0), (d0 * w).sum(0)
            t = t1 + t0; m = t > 0
            bs.append(np.sum(e1[m] * t0[m] / t[m]) / np.sum(e0[m] * t1[m] / t[m]))
        out[n]["ci95_bootstrap_agentday"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    # Kramers plot: escape rate vs kick rate per agent-day
    s = B["s"]
    adk = B["adid"].astype(np.int64)
    nad = B["ad"].height
    idle_min = np.bincount(adk, minlength=nad) * BIN / 60
    esc = np.bincount(adk, weights=B["event"], minlength=nad)
    # number of kicks during idle time: count messages in each bin (not just presence)
    lo = B["adid"] * BIG + B["boff"] + SHIFT; hi = lo + BIN
    nk = np.searchsorted(B["keys"]["any"], hi) - np.searchsorted(B["keys"]["any"], lo)
    kicks_ad = np.bincount(adk, weights=nk, minlength=nad)
    m = idle_min >= 10
    r_, k_ = kicks_ad[m] / idle_min[m], esc[m] / idle_min[m]
    q = np.quantile(r_, np.linspace(0, 1, 11))
    qb = np.clip(np.searchsorted(q, r_, side="right") - 1, 0, 9)
    curve = [{"r_mid": float(np.median(r_[qb == i])), "k": float(esc[m][qb == i].sum() / idle_min[m][qb == i].sum()),
              "agent_days": int((qb == i).sum())} for i in range(10)]
    X = np.c_[np.ones(m.sum()), r_]
    W = idle_min[m]
    beta = np.linalg.lstsq(X * np.sqrt(W)[:, None], k_ * np.sqrt(W), rcond=None)[0]
    rho = stats.spearmanr(r_, k_)
    out["kramers_agentday"] = {"agent_days": int(m.sum()), "k0_per_min": float(beta[0]), "c_per_kick": float(beta[1]),
                               "spearman_r_k": float(rho.statistic), "spearman_p": float(rho.pvalue), "curve": curve}
    e6c[reg] = out
    haz_store[reg] = (B, curve)
    print(reg, "done hazard", flush=True)
R["E6c_kicks"] = e6c

# ------------------------------------------------------------------ early pause terminations vs kicks (regime III)
pzx = (pz.filter(~pl.col("cens"))
       .with_columns((pl.col("realized") < pl.col("pause_s") - 30).alias("early"),
                     ((pl.col("t_next_row") - pl.col("win_start")).dt.total_seconds()).alias("off_wake")))
Bp = haz_store["III"][0]
adp = pzx.join(Bp["ad"], on=["agent", "pt_date"], how="left")
okp = adp["ad"].is_not_null().to_numpy()
adp = adp.filter(pl.col("ad").is_not_null())
ow, aid, er = adp["off_wake"].to_numpy(), adp["ad"].to_numpy().astype(np.float64), adp["early"].to_numpy()
kw = kicked(Bp["keys"]["any"], aid, ow, 60)
kw_m = kicked(Bp["keys"]["mention"], aid, ow, 60)
nullk = []
for it in range(N_NULL):
    mp = swap_map(Bp, RNG)
    nullk.append(kicked(Bp["keys"]["any"], mp[aid.astype(np.int64)], ow, 60)[er].mean())
R["E6b_early_wakes_vs_kicks"] = {
    "n_early": int(er.sum()), "n_on_time": int((~er).sum()),
    "frac_early_with_msg_in_prior_60s": float(kw[er].mean()), "frac_ontime_with_msg_in_prior_60s": float(kw[~er].mean()),
    "frac_early_with_mention_in_prior_60s": float(kw_m[er].mean()), "frac_ontime_with_mention_in_prior_60s": float(kw_m[~er].mean()),
    "null_dayswap_frac_early_with_msg": {"median": float(np.median(nullk)), "p95": float(np.percentile(nullk, 95))}}

# ------------------------------------------------------------------ peri-escape message density
peri = {}
for reg in ("I", "III"):
    B = haz_store[reg][0]
    s = B["s"].filter(~pl.col("cens"))
    t_esc = (s["off0"] + s["dwell"]).to_numpy(); aid = s["ad"].to_numpy().astype(np.float64)
    edges = np.arange(-600, 601, 20)
    def dens(aid_):
        h = np.zeros(len(edges) - 1)
        base = aid_ * BIG + t_esc + SHIFT
        for i in range(len(edges) - 1):
            h[i] = np.mean(np.searchsorted(B["keys"]["any"], base + edges[i + 1]) - np.searchsorted(B["keys"]["any"], base + edges[i]))
        return h / 20.0
    obs = dens(aid)
    nul = np.mean([dens(swap_map(B, RNG)[aid.astype(np.int64)]) for _ in range(20)], axis=0)
    peri[reg] = {"edges_s": edges.tolist(), "obs_msgs_per_s": obs.tolist(), "null_msgs_per_s": nul.tolist(),
                 "ratio_last60s_before_vs_null": float(obs[(edges[:-1] >= -60) & (edges[:-1] < 0)].mean() / nul[(edges[:-1] >= -60) & (edges[:-1] < 0)].mean()),
                 "ratio_last60s_before_vs_600_300s_before": float(obs[(edges[:-1] >= -60) & (edges[:-1] < 0)].mean() / obs[(edges[:-1] >= -600) & (edges[:-1] < -300)].mean())}
R["E6c_peri_escape"] = {r: {k2: v for k2, v in d.items() if k2.startswith("ratio")} for r, d in peri.items()}

# ------------------------------------------------------------------ E6d: by model family
e6d = {}
for reg in ("I", "III"):
    g = sp.filter(pl.col("reg") == reg)
    pa = (g.group_by("agent", "lab").agg(pl.col("dwell").median().alias("med"), pl.len().alias("n"), pl.col("cens").mean().alias("cf"))
          .filter((pl.col("n") >= 50) & (pl.col("med") > 0)).with_columns(pl.col("med").log().alias("lm")))
    grand = pa["lm"].mean()
    ss_tot = float(((pa["lm"] - grand) ** 2).sum())
    ss_lab = float(pa.group_by("lab").agg(pl.col("lm").mean().alias("m"), pl.len().alias("k")).select(((pl.col("m") - grand) ** 2 * pl.col("k")).sum()).item())
    bylab = (g.group_by("lab").agg(pl.len().alias("spells"), pl.col("agent").n_unique().alias("agents"), pl.col("dwell").median().alias("median_dwell_s"),
                                   (pl.col("dwell").filter(~pl.col("cens")).std() / pl.col("dwell").filter(~pl.col("cens")).mean()).alias("cv"))
             .sort("spells", descending=True))
    e6d[reg] = {"agents": pa.height, "lab_share_of_between_agent_var_log_median": ss_lab / ss_tot if ss_tot else None,
                "n_labs": int(pa["lab"].n_unique()), "by_lab": bylab.to_dicts()}
    # per-lab kick RR (any, tau 60)
    B = haz_store[reg][0]
    labs_bins = B["s"]["lab"].to_numpy()[B["sid"]]
    kk_ = kicked(B["keys"]["any"], B["adid"], B["boff"], TAU)
    km_ = kicked(B["keys"]["mention"], B["adid"], B["boff"], TAU)
    e6d[reg]["rr_any_by_lab"] = {}
    for lb in np.unique(labs_bins):
        mm = labs_bins == lb
        if B["event"][mm].sum() < 200:
            continue
        e6d[reg]["rr_any_by_lab"][lb] = {"rr_any": mh_rr(B["event"][mm], kk_[mm], B["stratum"][mm])[0],
                                         "rr_mention": mh_rr(B["event"][mm], km_[mm], B["stratum"][mm])[0],
                                         "escapes": int(B["event"][mm].sum())}
R["E6d_family"] = e6d

# ------------------------------------------------------------------ sensitivity: 'none'/'wait' turns do not end a spell
_, sp2 = make_spells({"pause", "none", "wait"})
R["E6_sensitivity_none_wait_not_escape_regimeIII_event_def"] = {
    reg: {"n": int(g.height), "median_s": float(g["dwell"].median()),
          "cv_uncens": float(g.filter(~pl.col("cens"))["dwell"].std() / g.filter(~pl.col("cens"))["dwell"].mean()),
          "best_tail_above_median": tail_fits(np.maximum(g["dwell"].to_numpy().astype(float), 1e-3), g["cens"].to_numpy(),
                                               float(np.median(g["dwell"].to_numpy()[g["dwell"].to_numpy() > 0])))["best_by_aic"]}
    for (reg,), g in sp2.filter(pl.col("reg") == "III").group_by("reg")}

# ------------------------------------------------------------------ figures
fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.2))
ax = axs[0]
for reg, col in (("I", "#3f6fb5"), ("III", "#c2662d")):
    g = sp.filter(pl.col("reg") == reg)
    x = np.sort(g["dwell"].to_numpy()); x = x[x > 0]
    ax.loglog(x, 1 - np.arange(len(x)) / len(x), lw=0.8, color=col, label=f"regime {reg} spells (n={len(x):,})")
    f = e6a[reg]["fits_above_median"]; xm = f["xmin_s"]; xx = np.logspace(np.log10(xm), np.log10(x.max()), 100)
    S0 = np.mean(x > xm)
    ln = f["lognormal"]; ax.loglog(xx, S0 * stats.norm.sf((np.log(xx) - ln["mu"]) / ln["sigma"]) / stats.norm.sf((np.log(xm) - ln["mu"]) / ln["sigma"]), ":", color=col, lw=0.7)
    a = f["power_law"]["alpha"]; ax.loglog(xx, S0 * (xx / xm) ** (1 - a), "--", color=col, lw=0.5, alpha=0.6)
ax.set_xlabel("idle spell dwell (s)"); ax.set_ylabel("P(dwell > t)"); ax.set_ylim(1e-5, 1.5)
ax.legend(frameon=False, fontsize=5); ax.set_title("dotted: lognormal; dashed: power law", fontsize=5.5)
ax = axs[1]
for reg, col in (("I", "#3f6fb5"), ("III", "#c2662d")):
    cv = haz_store[reg][1]
    ax.plot([c_["r_mid"] for c_ in cv], [c_["k"] for c_ in cv], "-o", ms=2, lw=0.8, color=col, label=f"regime {reg}")
ax.set_xlabel("kick rate while idle (room msgs / min)"); ax.set_ylabel("escape rate (per idle min)")
ax.legend(frameon=False, fontsize=6); ax.set_title("agent-day deciles", fontsize=6)
ax = axs[2]
for reg, col in (("I", "#3f6fb5"), ("III", "#c2662d")):
    p = peri[reg]; e = np.array(p["edges_s"]); mid = (e[:-1] + e[1:]) / 2
    ax.plot(mid, np.array(p["obs_msgs_per_s"]) * 60, color=col, lw=0.8, label=f"regime {reg}")
    ax.plot(mid, np.array(p["null_msgs_per_s"]) * 60, color=col, lw=0.6, ls="--", alpha=0.7)
ax.axvline(0, color="0.5", lw=0.4)
ax.set_xlabel("time relative to escape (s)"); ax.set_ylabel("room msgs / min"); ax.legend(frameon=False, fontsize=6)
ax.set_title("dashed: day-swap null", fontsize=6)
fig.tight_layout(); fig.savefig(FIG / "E6_idle_traps.pdf"); plt.close(fig)

(OUTD / "explore_e6_idle_traps.json").write_text(json.dumps(R, indent=1, default=str))
print(json.dumps({k_: v for k_, v in R.items()}, indent=1, default=str)[:20000])
