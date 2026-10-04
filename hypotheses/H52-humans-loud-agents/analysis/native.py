"""H52 period-native tests (card, "Eligible periods and native tests").

  n1  G04 within-call contrast: receiving calls holding both a human and an agent message of the same named status.
      Content: paired difference of chi_dd (human - agent) regressed on feature differences (novelty, log length,
      log read-out age); intercept = adjusted within-call premium. Reply: conditional choice between the two
      (exactly one is the parent of the recipient's reply), logit on feature differences; intercept = log-odds premium.
  n2  G51 role conflict: recipients with a #51 private role (goals.parquet agent_goal vectors, regime-III whitened);
      role alignment rho = cos(message, recipient role); premium (content, reply) in on-role vs off-role halves
      (period median split of rho) and their difference.
  n3  NE43: G51 before (<= 08-20) vs after (>= 08-21) the nudger stop: human premium per window and the
      difference; bot premium before.
  n4  Appointed / elected agent leaders (G35 lead designers, G44 temporary fine-tuned leader, G26 elected leader):
      leader-sent rows as their own class vs other-agent rows, next to the human premium.

Writes data/processed/H52-humans-loud-agents/native/<test>.json.
Usage: uv run python hypotheses/H52-humans-loud-agents/analysis/native.py n1 n2 n3 n4 [--B 1000]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402
import estimate as E  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

NAT = L.OUT / "native"


def day_boot(values_by_day: dict, fn, B: int, seed: int = L.SEED):
    days = sorted(values_by_day)
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(B):
        pick = rng.integers(len(days), size=len(days))
        out.append(fn([values_by_day[days[i]] for i in pick]))
    return out


def ols(X, y, w=None):
    if w is None:
        w = np.ones(len(y))
    W = np.sqrt(w)[:, None]
    return np.linalg.lstsq(X * W, y * W[:, 0], rcond=None)[0]


def logit_fit(X, y, iters=50, ridge=1e-3):
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ b))
        g = X.T @ (y - p) - ridge * b
        H = X.T @ (X * (p * (1 - p))[:, None]) + ridge * np.eye(X.shape[1])
        step = np.linalg.solve(H, g)
        b += step
        if np.abs(step).max() < 1e-8:
            break
    return b


# ------------------------------------------------------------------------------------------------ N1

def n1(B: int, period: str = "G04") -> dict:
    R = pl.read_parquet(L.OUT / period / "rows.parquet").filter(~pl.col("kickoff") & pl.col("cls").is_in([0, 1]))
    R = R.with_columns(pl.col("len").log1p().alias("lnlen"), pl.col("age_s").log1p().alias("lnage"))
    res = {"period": period}
    # pairs within call, same named status
    h = R.filter(pl.col("cls") == 1)
    a = R.filter(pl.col("cls") == 0)
    P = h.join(a, on=["turn_id", "named"], suffix="_a")
    res["n_calls_pairs"] = int(P["turn_id"].n_unique()); res["n_pairs"] = P.height
    res["named_share_pairs"] = float(P["named"].mean()) if P.height else None
    # content
    Pc = P.filter(pl.col("chi_dd").is_not_null() & pl.col("chi_dd_a").is_not_null() & pl.col("nov").is_not_null()
                  & pl.col("nov_a").is_not_null())
    if Pc.height > 30:
        y = (Pc["chi_dd"] - Pc["chi_dd_a"]).to_numpy()
        X = np.column_stack([np.ones(Pc.height), (Pc["nov"] - Pc["nov_a"]).to_numpy(),
                             (Pc["lnlen"] - Pc["lnlen_a"]).to_numpy(), (Pc["lnage"] - Pc["lnage_a"]).to_numpy()])
        # weight each call equally
        cnt = Pc.group_by("turn_id").len()
        w = 1 / Pc.join(cnt, on="turn_id", how="left")["len"].to_numpy()
        b = ols(X, y, w)
        dayv = {}
        dd = Pc["day_idx"].to_numpy()
        for d in np.unique(dd):
            m = dd == d
            dayv[d] = (X[m], y[m], w[m])
        bs = day_boot(dayv, lambda L_: ols(np.vstack([v[0] for v in L_]), np.concatenate([v[1] for v in L_]),
                                          np.concatenate([v[2] for v in L_]))[0], B)
        raw = float(np.average(y, weights=w))
        bs_raw = day_boot(dayv, lambda L_: float(np.average(np.concatenate([v[1] for v in L_]),
                                                            weights=np.concatenate([v[2] for v in L_]))), B)
        res["content"] = dict(adj=float(b[0]), adj_ci=L.ci(bs), raw=raw, raw_ci=L.ci(bs_raw), n_pairs=Pc.height,
                              n_calls=int(Pc["turn_id"].n_unique()), coef_nov=float(b[1]), coef_lnlen=float(b[2]),
                              coef_lnage=float(b[3]))
        # by named status
        for nm in (False, True):
            sub = Pc.filter(pl.col("named") == nm)
            if sub.height > 20:
                yy = (sub["chi_dd"] - sub["chi_dd_a"]).to_numpy()
                res["content"][f"raw_named_{nm}"] = dict(mean=float(yy.mean()), n=sub.height)
    # reply choice
    Pr = P.filter((pl.col("n_chat_post") >= 1) & (pl.col("rep") != pl.col("rep_a")) & pl.col("nov").is_not_null()
                  & pl.col("nov_a").is_not_null())
    if Pr.height > 30:
        y = Pr["rep"].cast(pl.Float64).to_numpy()   # 1 = the human message was chosen
        X = np.column_stack([np.ones(Pr.height), (Pr["nov"] - Pr["nov_a"]).to_numpy(),
                             (Pr["lnlen"] - Pr["lnlen_a"]).to_numpy(), (Pr["lnage"] - Pr["lnage_a"]).to_numpy()])
        b = logit_fit(X, y)
        dd = Pr["day_idx"].to_numpy()
        dayv = {d: (X[dd == d], y[dd == d]) for d in np.unique(dd)}
        bs = day_boot(dayv, lambda L_: logit_fit(np.vstack([v[0] for v in L_]), np.concatenate([v[1] for v in L_]))[0], B)
        res["reply_choice"] = dict(logodds_adj=float(b[0]), ci=L.ci(bs), p_human_raw=float(y.mean()),
                                   n_discordant=Pr.height, n_calls=int(Pr["turn_id"].n_unique()),
                                   odds_adj=float(np.exp(b[0])))
    L.jdump(res, NAT / "n1_G04_within_call.json")
    return res


# ------------------------------------------------------------------------------------------------ N2

def role_alignment(R: pl.DataFrame) -> np.ndarray:
    g = pl.read_parquet(L.ED / "goals.parquet").filter((pl.col("kind") == "agent_goal") & (pl.col("goal_no") == 51))
    GV = np.load(L.ED / "goal_vectors.npy").astype(np.float32)
    W = L.whitener("III", "bge_small")
    rv = {}
    for gid, ag, vf, vt in g.select("gid", "agent", "valid_from", "valid_to").iter_rows():
        rv.setdefault(int(ag), []).append((vf, vt or "9999", L.unit(W(GV[gid][None, :]))[0]))
    msgs = R["msg"].to_numpy().astype(np.int64)
    U = L.message_vectors(np.unique(msgs), "III")
    pos = {int(m): k for k, m in enumerate(np.unique(msgs))}
    Um = U[[pos[int(m)] for m in msgs]]
    rho = np.full(R.height, np.nan)
    for i, (a, d) in enumerate(R.select("recv", "pt_date").iter_rows()):
        for vf, vt, v in rv.get(int(a), []):
            if vf <= d < vt:
                rho[i] = float(Um[i] @ v)
                break
    return rho


def n2(B: int) -> dict:
    R = pl.read_parquet(L.OUT / "G51" / "rows.parquet")
    rho = role_alignment(R)
    R = R.with_columns(pl.Series("rho", rho).fill_nan(None))
    med = float(np.nanmedian(rho[(R["cls"].to_numpy() <= 1)]))
    res = {"rho_median": med, "rows_with_role": int(np.isfinite(rho).sum())}
    for half, flt in (("on_role", pl.col("rho") >= med), ("off_role", pl.col("rho") < med)):
        sub = R.filter(flt)
        d = E.prepare(sub, con_col="chi_dd")
        a = E.analyze(d, B=B, placebo_draws=0, regression=False, classes=(1,), outcomes=("con", "rep"))
        res[half] = {oc: a[oc]["human"]["all"] if "human" in a[oc] else {} for oc in ("con", "rep")}
        res[half]["agent_naming"] = {oc: a[oc]["agent_naming"] for oc in ("con", "rep")}
    # off-role tercile ("conflicts with the recipient's plan")
    t1 = float(np.nanquantile(rho[(R["cls"].to_numpy() <= 1)], 1 / 3))
    d = E.prepare(R.filter(pl.col("rho") < t1), con_col="chi_dd")
    a = E.analyze(d, B=B, placebo_draws=0, regression=False, classes=(1,), outcomes=("con", "rep"))
    res["bottom_tercile"] = {oc: a[oc].get("human", {}).get("all", {}) for oc in ("con", "rep")}
    # difference on - off with a joint day bootstrap via CEM sums
    res["diff_on_minus_off"] = {}
    for oc, col in (("con", "y_con"), ("rep", "y_rep")):
        dd = E.prepare(R, con_col="chi_dd")
        on = (dd["rho"].fill_null(np.nan).to_numpy() >= med)
        off = (dd["rho"].fill_null(np.nan).to_numpy() < med)
        y = dd[col].cast(pl.Float64).fill_null(np.nan).to_numpy()
        cls = dd["cls"].to_numpy(); s = dd["s_con"].to_numpy(); day = dd["day_idx"].to_numpy()
        S1 = L.cem_sums(y, (cls == 1) & on, (cls == 0) & on, s, day)
        S0 = L.cem_sums(y, (cls == 1) & off, (cls == 0) & off, s, day)
        days = np.unique(day)
        def pad(S):
            St, Nt, Sc, Nc, lab = S
            idx = np.searchsorted(days, lab)
            out = [np.zeros((len(days), St.shape[1])) for _ in range(4)]
            for o, X in zip(out, (St, Nt, Sc, Nc)):
                o[idx] = X
            return out
        A1, A0 = pad(S1), pad(S0)
        est = L.cem_att(*A1)[0] - L.cem_att(*A0)[0]
        rng = np.random.default_rng(L.SEED)
        bs = [L.cem_att(*A1, w)[0] - L.cem_att(*A0, w)[0] for w in L.boot_weights(len(days), B, rng)]
        res["diff_on_minus_off"][oc] = dict(diff=est, ci=L.ci(bs))
    L.jdump(res, NAT / "n2_G51_roles.json")
    return res


# ------------------------------------------------------------------------------------------------ N3

def n3(B: int) -> dict:
    R = pl.read_parquet(L.OUT / "G51" / "rows.parquet")
    res = {}
    pre = R.filter(pl.col("pt_date") <= "2026-08-20")
    post = R.filter(pl.col("pt_date") >= "2026-08-21")
    out_w = {}
    for tag, sub in (("before", pre), ("after", post)):
        d = E.prepare(sub, con_col="chi_dd")
        a = E.analyze(d, B=B, placebo_draws=0, regression=False, classes=(1, 2))
        out_w[tag] = a
        res[tag] = {oc: {c: a[oc].get(c, {}).get(E_sub(oc)) for c in ("human", "bot")} for oc in E.OUTCOMES}
        res[tag]["agent_naming"] = {oc: a[oc]["agent_naming"] for oc in E.OUTCOMES}
        res[tag]["n_days"] = int(sub["day_idx"].n_unique())
        res[tag]["human_msgs"] = int(sub.filter(pl.col("cls") == 1)["msg"].n_unique())
        res[tag]["bot_msgs"] = int(sub.filter(pl.col("cls") == 2)["msg"].n_unique())
    # difference after - before for the human premium (independent day sets: SEs add)
    res["diff_after_minus_before"] = {}
    for oc in E.OUTCOMES:
        b = res["before"][oc]["human"] or {}
        a = res["after"][oc]["human"] or {}
        if b.get("att") is not None and a.get("att") is not None and np.isfinite(b.get("se", np.nan)) and np.isfinite(a.get("se", np.nan)):
            dlt = a["att"] - b["att"]; se = float(np.hypot(a["se"], b["se"]))
            res["diff_after_minus_before"][oc] = dict(diff=dlt, se=se, ci=[dlt - 1.96 * se, dlt + 1.96 * se])
    L.jdump(res, NAT / "n3_NE43.json")
    return res


def E_sub(oc: str) -> str:
    return "all_bc" if oc == "act" else "all"


# ------------------------------------------------------------------------------------------------ N4

def leader_windows() -> list[tuple]:
    g = pl.read_parquet(L.SH / "ground_truth_labels.parquet").filter(
        (pl.col("label_kind") == "leader") & pl.col("preferred") & ~pl.col("holdout"))
    return [(int(gn), int(a), tf.timestamp(), tt.timestamp() if tt is not None else 9e12)
            for gn, a, tf, tt in g.select("goal_no", "agent", "t_valid_from", "t_valid_to").iter_rows()]


def n4(B: int) -> dict:
    wins = leader_windows()
    res = {}
    for period in ("G26", "G35", "G44"):
        p = L.OUT / period / "rows.parquet"
        if not p.exists():
            continue
        goal = int(period[1:])
        R = pl.read_parquet(p)
        snd = R["sender"].to_numpy(); tm = R["t_m"].to_numpy(); cls = R["cls"].to_numpy().copy()
        is_lead = np.zeros(R.height, bool)
        for gn, a, tf, tt in wins:
            if gn != goal:
                continue
            is_lead |= (cls == 0) & (snd == a) & (tm >= tf) & (tm < tt)
        cls[is_lead] = 3
        R2 = R.with_columns(pl.Series("cls", cls.astype(np.int8)))
        d = E.prepare(R2, con_col="chi_dd")
        a = E.analyze(d, B=B, placebo_draws=0, regression=False, classes=(3, 1))
        res[period] = {oc: {c: a[oc].get(c, {}).get(E_sub(oc)) for c in ("leader", "human")} for oc in E.OUTCOMES}
        res[period]["agent_naming"] = {oc: a[oc]["agent_naming"] for oc in E.OUTCOMES}
        res[period]["leader_rows"] = int(is_lead.sum())
        res[period]["leader_msgs"] = int(R2.filter(pl.col("cls") == 3)["msg"].n_unique())
        res[period]["human_msgs"] = int(R2.filter((pl.col("cls") == 1) & ~pl.col("kickoff"))["msg"].n_unique())
        # leader messages before vs during the leader window by the same agent (a within-agent check)
        same = [a_ for gn, a_, _, _ in wins if gn == goal]
        res[period]["leader_agents"] = sorted(set(same))
    L.jdump(res, NAT / "n4_leaders.json")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tests", nargs="+")
    ap.add_argument("--B", type=int, default=1000)
    a = ap.parse_args()
    NAT.mkdir(parents=True, exist_ok=True)
    for t in a.tests:
        r = {"n1": n1, "n2": n2, "n3": n3, "n4": n4}[t](a.B)
        print(t, "done", flush=True)


if __name__ == "__main__":
    main()
