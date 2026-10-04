"""H30 synthetic validation (axis F): can the gauge recover a known per-day susceptibility at village sampling?

Simulated swarm (one 'period' per replicate):
- agents: active/inactive per minute; stay-active prob p_i; inactive -> active hazard h0_i (1 + d/5)^-0.6 (aging idle
  spells, H16); declared pauses on half the idle spells; staggered day starts.
- nudger: fires on agents idle >= 20 min, refractory 45 min per agent (selection on idleness = rival R2); 25% of nudges
  name a second idle agent. Humans: Poisson messages to the whole room, 35% naming one agent.
- response (delayed, context-mediated, H04): a kick multiplies the target's activation hazard and stay-active odds by
  (1 + g) during tau in [4, 16) min. g = g_class(day) * (1 - phi * fill/41) * a_i, fill = turns since the agent's last
  reset (one turn per active minute, reset at 41). Bystanders: g = 0.
- content: whitened 32-d anisotropic OU states; statements when active; a kick read at the first active minute >= 2 min
  later shifts the state along the message direction by c_class(day) (same fill factor). Nudge directions = template +
  rho * (the target's recent statements, rival R3) + nu * specific part; human directions are random topics.
- truth per kick from common-random-number counterfactuals (the same day without that kick): extra active minutes in
  tau = 1..30, and the change of post-kick statement projections on the message direction.

Writes data/processed/H30-operator-susceptibility/synthetic/{synthetic_results.json, replicates.parquet} and
figures/synthetic_validation.pdf. Run: uv run python hypotheses/H30-operator-susceptibility/analysis/synthetic.py [--reps N]
"""
from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h30lib import *  # noqa: E402,F403

D_DELAY, L_RESP = 4, 12
DIM = 32
LAM = 1.0 / np.arange(1, DIM + 1) ** 1.2      # anisotropic content spectrum (few effective dims, H20)
LAM = LAM / LAM.sum() * 8.0

DESIGNS = {
    # n_agents, minutes/day, days, nudges/day target, human msgs/day, nudge template specificity nu
    "G51like": dict(n_agents=16, n_min=480, n_days=20, nudges=16.0, humans=2.5, nu=0.15),
    "G38like": dict(n_agents=12, n_min=240, n_days=17, nudges=6.5, humans=1.6, nu=0.6),
    "G05like": dict(n_agents=4, n_min=120, n_days=5, nudges=0.0, humans=150.0, nu=0.6),
}
# extra design for the isolation check only: the nudger re-nudges idle agents after 15 min (real #51: 52% of nudges are
# followed by another directed kick to the same agent within 60 min)
DESIGNS_EXTRA = {"G51renudge": dict(n_agents=16, n_min=480, n_days=20, nudges=16.0, humans=2.5, nu=0.15, refractory=15)}
G0 = 0.9          # nudge hazard multiplier (true A30 ~ 1.8 min per nudge at G51-like sampling)
C0 = 0.6          # content kick size (state units); gives ~0.05-0.1 cosine on post statements


def scenario_params(name: str, n_days: int, rng) -> dict:
    d = np.arange(n_days)
    one = np.ones(n_days)
    if name == "S0_null":
        return dict(gN=0 * one, gHu=0 * one, gHm=0 * one, cN=0 * one, cH=0 * one, phi=0.0, rho=0.6)
    if name == "S1_const":
        return dict(gN=G0 * one, gHu=0.35 * G0 * one, gHm=1.5 * G0 * one, cN=0.0 * one, cH=C0 * one, phi=0.0, rho=0.6)
    if name == "S2_hetero":
        f = np.exp(rng.normal(0, 0.6, n_days)); f /= f.mean()
        fc = np.exp(rng.normal(0, 0.6, n_days)); fc /= fc.mean()
        return dict(gN=G0 * f, gHu=0.35 * G0 * f, gHm=1.5 * G0 * f, cN=0.5 * C0 * fc, cH=C0 * fc, phi=0.0, rho=0.6)
    if name == "S3_aging":
        f = 1.6 * (1 - 0.7 * d / max(1, n_days - 1)) / 1.25
        return dict(gN=G0 * f, gHu=0.35 * G0 * f, gHm=1.5 * G0 * f, cN=0.5 * C0 * f, cH=C0 * f, phi=0.0, rho=0.6)
    if name == "S5_dayshock":
        # constant response, but every day has its own swarm-wide baseline activity level (a day field)
        return dict(gN=G0 * one, gHu=0.35 * G0 * one, gHm=1.5 * G0 * one, cN=0.0 * one, cH=C0 * one, phi=0.0, rho=0.6,
                    dayshock=np.exp(rng.normal(0, 0.5, n_days)))
    if name == "S4_fill":
        return dict(gN=1.6 * G0 * one, gHu=0.5 * G0 * one, gHm=2.0 * G0 * one, cN=0.5 * C0 * one, cH=1.4 * C0 * one,
                    phi=0.8, rho=0.6)
    raise ValueError(name)


def human_dense_adjust(par: dict) -> dict:
    """In the dense-chat design each message is a much weaker kick (100+ messages a day)."""
    p = dict(par)
    p["gHu"] = par["gHu"] * 0.06
    p["gHm"] = par["gHm"] * 0.3
    return p


def simulate(design: str, scen: str, seed: int):
    cfg = DESIGNS.get(design) or DESIGNS_EXTRA[design]
    rng = np.random.default_rng(seed)
    nA, T, nD = cfg["n_agents"], cfg["n_min"], cfg["n_days"]
    par = scenario_params(scen, nD, rng)
    if design == "G05like":
        par = human_dense_adjust(par)
    p_stay = rng.uniform(0.80, 0.92, nA)
    h0 = rng.uniform(0.04, 0.15, nA)
    afac = np.exp(rng.normal(0, 0.3, nA))
    field_ = rng.normal(0, 1, (nA, DIM)) * np.sqrt(LAM) * 1.2
    template = rng.normal(0, 1, DIM) * np.sqrt(LAM); template /= np.linalg.norm(template)
    theta, sig = 1 / 90.0, 0.6
    q_nudge = cfg["nudges"] / (nA * T * 0.25) if cfg["nudges"] > 0 else 0.0
    lam_h = cfg["humans"] / T
    panels, kick_rows, msg_rows = [], [], []
    stmt_t = {a: [] for a in range(nA)}; stmt_v = {a: [] for a in range(nA)}
    U_list = []
    x = field_ + rng.normal(0, 1, (nA, DIM)) * np.sqrt(LAM) * sig
    fillc = rng.integers(0, 41, nA).astype(float)
    msg_id = 0
    for day in range(nD):
        start = rng.integers(0, 16, nA)
        act = np.zeros((nA, T), np.int8); idle = np.zeros((nA, T), np.int8)
        U1 = rng.random((nA, T)); U2 = rng.random((nA, T)); Us = rng.random((nA, T))
        mult = np.ones((nA, T + 64))
        last_active = np.full(nA, -1)
        in_pause = np.zeros(nA, bool)
        last_nudge = np.full(nA, -10 ** 6)
        fill_at = np.zeros((nA, T))
        kicks_today = []     # (agent, minute, cls, msg, g, c)
        pending_read = []    # content kicks awaiting the agent's next active minute: [agent, minute_ready, u, c, k_index]
        xs = np.zeros((T, nA, DIM), np.float32)
        noise = rng.normal(0, 1, (T, nA, DIM)) * np.sqrt(LAM) * sig * np.sqrt(2 * theta)
        stmt_noise = rng.normal(0, 1, (T, nA, DIM)) * np.sqrt(LAM) * 0.5
        recent = [[] for _ in range(nA)]  # recent statement vectors (minute, vec)
        for m in range(T):
            started = m >= start
            prev = act[:, m - 1] if m > 0 else np.zeros(nA, np.int8)
            d_idle = np.where(last_active >= 0, m - 1 - last_active, m - start)
            haz = h0 * par.get("dayshock", np.ones(nD))[day] * (1 + np.maximum(d_idle, 0) / 5.0) ** -0.6 * mult[:, m]
            ps = 1 - (1 - p_stay) / mult[:, m]
            new = np.where(prev == 1, U1[:, m] < ps, U1[:, m] < np.minimum(haz, 0.95)).astype(np.int8)
            new[~started] = 0
            # pause flag: set at the start of an inactive spell
            spell_start = (prev == 1) & (new == 0)
            in_pause = np.where(spell_start, U2[:, m] < 0.5, in_pause)
            in_pause[new == 1] = False
            act[:, m] = new
            idle[:, m] = (in_pause & (new == 0) & started).astype(np.int8)
            fill_at[:, m] = fillc
            fillc = np.where(new == 1, fillc + 1, fillc)
            fillc = np.where(fillc >= 41, 0, fillc)
            last_active = np.where(new == 1, m, last_active)
            # content state
            x = x + theta * (field_ - x) + noise[m]
            # read pending content kicks
            keep = []
            for pr in pending_read:
                a_, ready, u, c, kidx = pr
                if m >= ready and new[a_] == 1:
                    vec = c * u * 1.0
                    x[a_] += vec
                    kicks_today[kidx][6] = m
                else:
                    keep.append(pr)
            pending_read = keep
            xs[m] = x
            emit = (new == 1) & (Us[:, m] < 0.12)
            for a_ in np.nonzero(emit)[0]:
                v = x[a_] + stmt_noise[m, a_]
                v = v / np.linalg.norm(v)
                ts_ = day * 86400.0 + m * 60.0 + 20.0
                stmt_t[a_].append(ts_); stmt_v[a_].append(v.astype(np.float32))
                recent[a_].append((m, v))
            # ---- kicks generated at minute m (take effect from m + D)
            ks = []
            if q_nudge > 0 and m >= 20:
                elig = np.nonzero((new == 0) & started & (d_idle >= 20) & (m - last_nudge >= cfg.get("refractory", 45)))[0]
                for a_ in elig:
                    if rng.random() < q_nudge * 1.4:
                        tg = [a_]
                        others = [b for b in elig if b != a_]
                        if others and rng.random() < 0.25:
                            tg.append(int(rng.choice(others)))
                        for b in tg:
                            last_nudge[b] = m
                        rec = [r_ for r_ in recent[a_] if m - r_[0] <= 60]
                        rv = np.mean([r_[1] for r_ in rec], 0) if rec else np.zeros(DIM)
                        rvn = rv / np.linalg.norm(rv) if np.linalg.norm(rv) > 0 else rv
                        spec = rng.normal(0, 1, DIM) * np.sqrt(LAM); spec /= np.linalg.norm(spec)
                        u = template + par["rho"] * rvn + cfg["nu"] * spec
                        u = u / np.linalg.norm(u)
                        ks.append(("nudge", tg, u))
                        break   # at most one nudge per minute
            nh = rng.poisson(lam_h)
            for _ in range(nh):
                u = rng.normal(0, 1, DIM) * np.sqrt(LAM); u /= np.linalg.norm(u)
                tg = [int(rng.integers(nA))] if rng.random() < 0.35 else []
                ks.append(("human", tg, u))
            for kind, tg, u in ks:
                U_list.append(u.astype(np.float32))
                msg_rows.append((msg_id, day, kind, list(map(int, tg))))
                rec_agents = np.nonzero(started)[0] if kind == "human" else np.nonzero(started)[0]
                for a_ in rec_agents:
                    if kind == "nudge":
                        cls = "N_tgt" if a_ in tg else "N_by"
                        g = par["gN"][day] if cls == "N_tgt" else 0.0
                        c = par["cN"][day] if cls == "N_tgt" else 0.0
                    else:
                        cls = "H_men" if a_ in tg else "H_und"
                        g = (par["gHm"] if cls == "H_men" else par["gHu"])[day]
                        c = par["cH"][day] * (2.0 if cls == "H_men" else 1.0)
                    fac = (1 - par["phi"] * min(fillc[a_] / 41.0, 1.0)) * afac[a_]
                    g_eff, c_eff = g * fac, c * fac
                    if g_eff != 0:
                        mult[a_, m + D_DELAY:m + D_DELAY + L_RESP] += g_eff
                    kidx = len(kicks_today)
                    kicks_today.append([int(a_), m, cls, msg_id, g_eff, c_eff, -1, kind, float(fillc[a_])])
                    if c_eff != 0:
                        pending_read.append([int(a_), m + 2, u, c_eff, kidx])
                msg_id += 1
        # ---- truth: CRN counterfactual per kick (activity), conditional content truth
        for k in kicks_today:
            a_, m0, cls, mid, g_eff, c_eff, mread, kind, fl = k
            e_act = 0.0
            if g_eff != 0:
                mcf = mult[a_].copy()
                mcf[m0 + D_DELAY:m0 + D_DELAY + L_RESP] -= g_eff
                st_prev = act[a_, m0]
                la = m0 if st_prev == 1 else (np.max(np.nonzero(act[a_, :m0 + 1])[0]) if act[a_, :m0 + 1].any() else -1)
                tot = 0
                for mm in range(m0 + 1, min(T, m0 + H + 1)):
                    dI = (mm - 1 - la) if la >= 0 else (mm - start[a_])
                    hz = h0[a_] * par.get("dayshock", np.ones(nD))[day] * (1 + max(dI, 0) / 5.0) ** -0.6 * mcf[mm]
                    pss = 1 - (1 - p_stay[a_]) / mcf[mm]
                    nw = int(U1[a_, mm] < pss) if st_prev == 1 else int(U1[a_, mm] < min(hz, 0.95))
                    if mm < start[a_]:
                        nw = 0
                    tot += act[a_, mm] - nw
                    st_prev = nw
                    if nw:
                        la = mm
                e_act = float(tot)
            e_con = np.nan
            u = U_list[mid]
            ts0 = day * 86400.0 + m0 * 60.0 + 30.0
            T_ = np.array(stmt_t[a_]) if stmt_t[a_] else np.zeros(0)
            if len(T_):
                post = np.nonzero((T_ > ts0) & (T_ <= ts0 + CON_WIN_S))[0][:CON_KMAX]
                if len(post):
                    if c_eff != 0 and mread >= 0:
                        diffs = []
                        for j in post:
                            mj = int((T_[j] - day * 86400.0 - 20.0) // 60)
                            if mj < mread:
                                diffs.append(0.0); continue
                            # remove this kick's jump, relaxed by the OU decay since reading
                            decay = (1 - theta) ** (mj - mread)
                            vf = stmt_v[a_][j]
                            raw_f = xs[mj, a_] + stmt_noise[mj, a_]
                            raw_c = raw_f - c_eff * u * decay
                            diffs.append(float(raw_f @ u / np.linalg.norm(raw_f) - raw_c @ u / np.linalg.norm(raw_c)))
                        e_con = float(np.mean(diffs))
                    else:
                        e_con = 0.0
            kick_rows.append((day, a_, a_, m0, cls, mid, kind, ts0, e_act, e_con, fl, g_eff, c_eff))
        panels.append(Panel(day=day, act=act, idle=idle, agents=np.arange(nA), label=f"d{day:02d}", goal_day=day))
    kicks = pl.DataFrame(kick_rows, schema={"day": pl.Int32, "row": pl.Int32, "agent": pl.Int32, "minute": pl.Int32,
                                            "cls": pl.Utf8, "msg": pl.Int64, "kind": pl.Utf8, "ts": pl.Float64,
                                            "e_act": pl.Float64, "e_con": pl.Float64, "fill": pl.Float64,
                                            "g": pl.Float64, "c": pl.Float64}, orient="row")
    msg_meta = pl.DataFrame(msg_rows, schema={"msg": pl.Int64, "day": pl.Int32, "kind": pl.Utf8, "targets": pl.List(pl.Int64)},
                            orient="row")
    U = np.array(U_list, np.float32) if U_list else np.zeros((0, DIM), np.float32)
    st_t = {a: np.array(v) for a, v in stmt_t.items() if v}
    st_v = {a: np.array(stmt_v[a]) for a in st_t}
    return panels, kicks, msg_meta, U, st_t, st_v, par


def corr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[ok], b[ok])[0, 1]) if ok.sum() >= 4 and np.std(a[ok]) > 0 and np.std(b[ok]) > 0 else np.nan


def evaluate(design: str, scen: str, seed: int, n_swap: int = 4) -> dict:
    t0 = time.time()
    panels, kicks, mm, U, st_t, st_v, par = simulate(design, scen, seed)
    base = build_base(panels, kicks=kicks)
    X = kick_columns(base, kicks)
    fit = fit_activity(base, X)                    # A2 default: strata + day fixed effects
    fit0 = fit_activity(base, X, fe2=None)         # as pre-registered: strata only
    W = boot_weights(len(panels), 400, seed)
    pc = period_ci(fit, W)
    pre = fit_activity(base, X, outcome="Ypre")
    out = {"design": design, "scen": scen, "seed": seed}
    out["act_N_tgt_est_nofe"] = fit0.coef("N_tgt") if "N_tgt" in fit0.classes and np.isfinite(fit0.beta[0]) else np.nan
    out["act_H_und_est_nofe"] = fit0.coef("H_und")
    truth_cls = kicks.group_by("cls").agg(pl.col("e_act").mean().alias("t"), pl.len().alias("n"))
    tmap = {c: (t, n) for c, t, n in truth_cls.iter_rows()}
    for c in CLASSES:
        if c in pc:
            out[f"act_{c}_est"], out[f"act_{c}_lo"], out[f"act_{c}_hi"] = pc[c]
            out[f"act_{c}_true"], out[f"act_{c}_n"] = tmap.get(c, (np.nan, 0))
            out[f"pre_{c}"] = pre.coef(c) if c in pre.classes else np.nan
    # day-swap null
    pres = {p.day: {int(a): i for i, a in enumerate(p.agents)} for p in panels}
    rng = np.random.default_rng(seed + 7)
    sw = []
    for _ in range(n_swap):
        ks = day_swap(kicks, pres, rng)
        b2 = build_base(panels, kicks=ks)
        f2 = fit_activity(b2, kick_columns(b2, ks))
        sw.append({c: f2.coef(c) for c in CLASSES if np.isfinite(f2.beta[CLASSES.index(c)])})
    for c in CLASSES:
        v = [s[c] for s in sw if c in s]
        out[f"swap_{c}"] = float(np.mean(v)) if v else np.nan
    # daily activity gauge vs daily truth
    dly = daily_activity(fit)
    tday = kicks.group_by("day", "cls").agg(pl.col("e_act").mean().alias("t"))
    dj = dly.join(tday, on=["day", "cls"], how="left")
    main = "N_tgt" if design != "G05like" else "H_und"
    dm = dj.filter((pl.col("cls") == main) & (pl.col("n") >= 3))
    if dm.height >= 4:
        out["daily_corr"] = corr(dm["chi"], dm["t"])
        cov = ((dm["chi"] - 1.96 * dm["se"] <= dm["t"]) & (dm["t"] <= dm["chi"] + 1.96 * dm["se"])).mean()
        out["daily_cover"] = float(cov)
        kvm = fit.kick_r.filter(pl.col("cls") == main).join(
            kicks.unique(["day", "row", "minute", "cls"]).select("day", "row", "minute", "cls", pl.col("msg").alias("cluster")),
            on=["day", "row", "minute", "cls"], how="left")
        st = stability(dm.select("day", "n", "chi", "se"), kick_values=kvm)
        dm0 = daily_activity(fit0).filter((pl.col("cls") == main) & (pl.col("n") >= 3))
        kv0 = fit0.kick_r.filter(pl.col("cls") == main).join(
            kicks.unique(["day", "row", "minute", "cls"]).select("day", "row", "minute", "cls", pl.col("msg").alias("cluster")),
            on=["day", "row", "minute", "cls"], how="left")
        st0 = stability(dm0.select("day", "n", "chi", "se"), kick_values=kv0)
        out["stab_nofe_p_perm_msg"] = st0.get("p_perm_msg"); out["stab_nofe_R1_perm_msg"] = st0.get("R1_perm_msg")
        out.update({f"stab_{k}": v for k, v in st.items() if isinstance(v, (int, float)) or v is None})
        # true reliability: variance of true daily means vs median sampling variance
        tv = float(np.var(dm["t"].to_numpy(), ddof=1))
        out["true_R1"] = tv / (tv + float(np.median(dm["se"].to_numpy() ** 2)))
    # aging and fill slopes on per-kick contributions (agent FE, day clusters)
    kr = fit.kick_r.filter(pl.col("cls") == main).join(kicks.select("day", "row", "minute", "cls", "fill", "e_act")
                                                       .unique(["day", "row", "minute", "cls"]),
                                                       on=["day", "row", "minute", "cls"], how="left")
    if kr.height > 20:
        y = kr["r"].to_numpy(); w = kr["w"].to_numpy(); ag = kr["agent"].to_numpy(); dd = kr["day"].to_numpy().astype(float)
        s1 = wls_slope(y, dd, w, groups=ag, clusters=kr["day"].to_numpy())
        s1t = wls_slope(kr["e_act"].to_numpy(), dd, np.ones(len(y)), groups=ag, clusters=kr["day"].to_numpy())
        out["age_slope_est"], out["age_slope_lo"], out["age_slope_hi"] = s1.get("slope"), s1.get("lo"), s1.get("hi")
        out["age_slope_true"] = s1t.get("slope")
        fl = kr["fill"].to_numpy()
        s2 = wls_slope(y, fl, w, groups=ag, clusters=kr["day"].to_numpy())
        s2t = wls_slope(kr["e_act"].to_numpy(), fl, np.ones(len(y)), groups=ag, clusters=kr["day"].to_numpy())
        out["fill_slope_est"], out["fill_slope_lo"], out["fill_slope_hi"] = s2.get("slope"), s2.get("lo"), s2.get("hi")
        out["fill_slope_true"] = s2t.get("slope")
    # content channel
    pairs = kicks.with_row_index("pair").with_columns(pl.col("pair").cast(pl.Int64))
    P, Q, npre, npost, Sp = pre_post_means(st_t, st_v, pairs)
    cs = content_scores(pairs, P, Q, U, mm, S=Sp, rng=np.random.default_rng(seed + 11))
    for c in CLASSES:
        sub = cs.filter((pl.col("cls") == c) & pl.col("chi_orth").is_not_nan())
        if sub.height >= 10:
            out[f"con_{c}_n"] = sub.height
            out[f"con_{c}_est"] = float(sub["chi"].mean())
            out[f"con_{c}_se"] = float(sub["chi"].std() / np.sqrt(sub.height))
            out[f"con_{c}_unm"] = float(sub["chi_unm"].mean())
            out[f"con_{c}_raw"] = float(sub["d_true"].mean())
            out[f"con_{c}_null"] = float(sub["chi_null"].mean())
            for v_ in ("chi_reg", "chi_orth", "chi_reg_null", "chi_orth_null"):
                out[f"con_{c}_{v_}"] = float(sub[v_].drop_nans().mean()) if sub[v_].drop_nans().len() else np.nan
            out[f"con_{c}_true"] = float(sub["e_con"].drop_nans().mean())
    cmain = "N_tgt" if design == "G51like" else ("N_tgt" if design == "G38like" else "H_und")
    for cm_ in ([cmain, "H_und"] if design != "G05like" else ["H_und", "H_men"]):
        sub = cs.filter((pl.col("cls") == cm_) & pl.col("chi_orth").is_not_nan())
        if sub.height < 20:
            continue
        dmc = daily_mean(sub, "chi_orth").filter(pl.col("n") >= 3)
        tdc = sub.group_by("day").agg(pl.col("e_con").mean().alias("t"))
        dmc = dmc.join(tdc, on="day", how="left")
        if dmc.height >= 4:
            out[f"con_daily_corr_{cm_}"] = corr(dmc["chi"], dmc["t"])
            stc = stability(dmc.select("day", "n", "chi", "se"),
                            kick_values=sub.select("day", "agent", pl.col("msg").alias("cluster"), pl.col("chi_orth").alias("r")),
                            weight_col=None)
            out[f"con_stab_R1_{cm_}"] = stc.get("R1"); out[f"con_stab_pQ_{cm_}"] = stc.get("p_Q")
            out[f"con_stab_R1perm_{cm_}"] = stc.get("R1_perm"); out[f"con_stab_pperm_{cm_}"] = stc.get("p_perm")
            out[f"con_stab_R1permmsg_{cm_}"] = stc.get("R1_perm_msg"); out[f"con_stab_ppermmsg_{cm_}"] = stc.get("p_perm_msg")
            out[f"con_true_R1_{cm_}"] = float(np.var(dmc["t"].to_numpy(), ddof=1) /
                                              (np.var(dmc["t"].to_numpy(), ddof=1) + np.median(dmc["se"].to_numpy() ** 2)))
    out["secs"] = time.time() - t0
    return out


def run(args):
    return evaluate(*args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=8)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    jobs = []
    for design in DESIGNS:
        scens = ["S0_null", "S1_const", "S2_hetero", "S3_aging", "S4_fill", "S5_dayshock"]
        reps = a.reps if design != "G05like" else max(4, a.reps)
        for scen in scens:
            if a.only and a.only not in (design, scen):
                continue
            for r in range(reps):
                jobs.append((design, scen, 1000 * (list(DESIGNS).index(design) + 1) + 100 * scens.index(scen) + r))
    out_dir = OUT / "synthetic"
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    res = []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for i, r in enumerate(ex.map(run, jobs)):
            res.append(r)
            if i % 5 == 0:
                print(f"{i + 1}/{len(jobs)} {r['design']} {r['scen']} {r['secs']:.0f}s (elapsed {time.time() - t0:.0f}s)", flush=True)
    df = pl.DataFrame(res, infer_schema_length=None)
    df.write_parquet(out_dir / "replicates.parquet")
    summary = summarize(df)
    jdump(summary, out_dir / "synthetic_results.json")
    write_provenance(out_dir, "hypotheses/H30-operator-susceptibility/analysis/synthetic.py", [],
                     {"reps": a.reps, "designs": DESIGNS, "G0": G0, "C0": C0, "delay": D_DELAY, "resp_len": L_RESP})
    print(json.dumps(summary, indent=1, default=str)[:6000])


def summarize(df: pl.DataFrame) -> dict:
    out = {}
    for (design, scen), g in df.group_by(["design", "scen"], maintain_order=True):
        s = {"reps": g.height}
        for c in CLASSES:
            if f"act_{c}_est" in g.columns and g[f"act_{c}_est"].drop_nulls().len():
                est = g[f"act_{c}_est"].to_numpy().astype(float); tru = g[f"act_{c}_true"].to_numpy().astype(float)
                lo = g[f"act_{c}_lo"].to_numpy().astype(float); hi = g[f"act_{c}_hi"].to_numpy().astype(float)
                s[f"act_{c}"] = {"est_mean": float(np.nanmean(est)), "true_mean": float(np.nanmean(tru)),
                                 "bias": float(np.nanmean(est - tru)), "rmse": float(np.sqrt(np.nanmean((est - tru) ** 2))),
                                 "cover": float(np.nanmean((lo <= tru) & (tru <= hi))),
                                 "excl0": float(np.nanmean((lo > 0) | (hi < 0))),
                                 "pre_placebo": float(np.nanmean(g[f"pre_{c}"].to_numpy().astype(float))),
                                 "swap_null": float(np.nanmean(g[f"swap_{c}"].to_numpy().astype(float)))
                                 if f"swap_{c}" in g.columns else None}
            if f"con_{c}_est" in g.columns and g[f"con_{c}_est"].drop_nulls().len():
                s[f"con_{c}"] = {k: float(np.nanmean(g[f"con_{c}_{k}"].to_numpy().astype(float)))
                                 for k in ("est", "se", "unm", "raw", "null", "true", "n", "chi_reg", "chi_orth", "chi_reg_null", "chi_orth_null")
                                 if f"con_{c}_{k}" in g.columns}
        for k in ("daily_corr", "daily_cover", "stab_R1", "stab_R1_perm", "stab_R1_perm_msg", "stab_R1_perm_agent", "true_R1",
                  "stab_p_Q", "stab_p_perm", "stab_p_perm_msg", "stab_p_perm_agent", "stab_lag1",
                  "stab_nofe_p_perm_msg", "stab_nofe_R1_perm_msg", "act_N_tgt_est_nofe", "act_H_und_est_nofe",
                  "stab_p_lag1", "stab_split_half_SB",
                  "age_slope_est", "age_slope_true", "fill_slope_est", "fill_slope_true"):
            if k in g.columns:
                v = g[k].to_numpy().astype(float)
                s[k] = float(np.nanmean(v))
                if k in ("stab_p_Q", "stab_p_perm", "stab_p_perm_msg", "stab_p_perm_agent", "stab_p_lag1", "stab_nofe_p_perm_msg"):
                    s[k + "_rej05"] = float(np.nanmean(v < 0.05))
        for k in ("age_slope", "fill_slope"):
            if f"{k}_lo" in g.columns:
                lo = g[f"{k}_lo"].to_numpy().astype(float); hi = g[f"{k}_hi"].to_numpy().astype(float)
                s[k + "_neg_sig"] = float(np.nanmean(hi < 0)); s[k + "_pos_sig"] = float(np.nanmean(lo > 0))
        for k in [c for c in g.columns if c.startswith("con_daily_corr") or c.startswith("con_stab") or c.startswith("con_true")]:
            v = g[k].to_numpy().astype(float)
            s[k] = float(np.nanmean(v))
            if "pQ" in k or "pperm" in k or "ppermmsg" in k:
                s[k + "_rej05"] = float(np.nanmean(v < 0.05))
        out[f"{design}|{scen}"] = s
    return out


if __name__ == "__main__":
    main()
