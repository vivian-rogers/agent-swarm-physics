"""H34 core: period inputs (real data) and the cascade assembler shared by real and synthetic data.

assemble(inp) turns marker uses on a message timeline into:
  first_uses  one row per (idea, agent) first use: status seed / exposed / unexposed, parent (most recent and earliest
              visible exposure), k_src, n_exp, lag in own talk turns, tree id, generation, offspring
  trees       one row per tree: idea, root agent, root type (invented / human / field), size, depth, censored
  atrisk      per (idea, k bin, turns-since-exposure bin): at-risk talk turns and adoptions (dose response)
  jitter      per non-seed agent first use: observed exposed / first-turn flags and their jitter-null probabilities
  roomx       per idea: agents active in the idea's first 24 h, split by ever-visibly-exposed, and their adoptions
Definitions are in ../README.md ("Operational definitions"). No text is used here: markers are hashes.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H34-idea-cascades"
# Round 1b (2026-10-04): H34_DATA=r1b switches visibility to the DQ1 context ledger and writes under OUT/r1b/.
# Default (unset) reproduces round 1 exactly (H18 call-start rule on the `exposure` room table).
R1B = os.environ.get("H34_DATA", "") == "r1b"
OUT_RUN = OUT / "r1b" if R1B else OUT
INF_US = np.iinfo(np.int64).max // 4
RECENT_US = 300 * 1_000_000      # round 1b H57 placebo: same-lag window for seen vs unread uses
US = 1_000_000
GUARD_US = 1 * US            # H18: the talk's own action mirror is logged ~0.06 s before AGENT_TALK
STALE_US = 6 * 3600 * US     # no turn within 6 h before a talk -> call start = t - 1 s (flagged)
DAY_US = 24 * 3600 * US
H_TURNS = 15                 # at-risk turns kept after the first visibly exposed turn
MEM_TURNS = 3                # recency window for k_recent (amendment A2): the agent's last 3 call windows
DELTAS_S = (1800, 3600, 7200)
KIND = {"agent": 0, "human": 1, "automated": 2}
ROOT_TYPES = {"invented": 0, "human": 1, "field": 2}
STATUS = {"seed": 0, "exposed": 1, "unexposed": 2}


# ------------------------------------------------------------------------------------------------ real-data inputs
class _EvShim:
    """Minimal stand-in for H18's Shared object: turn_times() only needs `.ev` (agent events: t, agent)."""

    def __init__(self, ev: pl.DataFrame):
        self.ev = ev


def _h18_turn_times():
    sys.path.insert(0, str(ROOT / "infra/shared"))
    sys.path.insert(0, str(ROOT / "hypotheses/H18-attention-dilution/scheme"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("h18_build", ROOT / "hypotheses/H18-attention-dilution/scheme/build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)   # import only; H18 code is never modified
    return mod.turn_times


def _us(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy().astype(np.int64)


class Shared:
    def __init__(self):
        sys.path.insert(0, str(ROOT / "infra/shared"))
        from common import holdout_mask
        self.holdout_mask = holdout_mask
        self.cal = pl.read_parquet(SH / "calendar.parquet")
        self.chat = pl.read_parquet(SH / "chat_core.parquet",
                                    columns=["t", "pt_date", "goal_no", "room", "speaker_kind", "agent", "human"]
                                    + (["message_id"] if R1B else [])).with_row_index("msg")
        self.exposure = pl.read_parquet(SH / "exposure.parquet", columns=["msg", "agent"])
        self.roster = pl.read_parquet(SH / "roster.parquet")
        self.cc = set(self.roster.filter(pl.col("claude_code"))["agent"].to_list())
        self.n_agents = int(self.roster["agent"].max()) + 1
        self.ev = (pl.read_parquet(SH / "events_core.parquet", columns=["t", "actor_kind", "agent"])
                   .filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null()).select("t", "agent"))
        self.turn_times = _h18_turn_times()
        self.uses = pl.read_parquet(OUT / "markers/uses.parquet")
        self.first_seen = pl.read_parquet(OUT / "markers/first_seen.parquet")

    def period_days(self, g: int, only_holdout: bool = False, allow_holdout: bool = False) -> list[str]:
        cal = self.cal.filter(pl.col("goal_no") == g)
        days = cal["pt_date"].to_list()
        hm = self.holdout_mask(days, [g] * len(days))
        hflag = cal["holdout"].fill_null(False).to_list()
        held = [a or b for a, b in zip(hm, hflag)]
        if only_holdout:
            return sorted(d for d, h in zip(days, held) if h)
        if allow_holdout:
            return sorted(days)
        return sorted(d for d, h in zip(days, held) if not h)


def period_inputs(sh: Shared, g: int, days: list[str] | None = None, uses: pl.DataFrame | None = None,
                  ideas: np.ndarray | None = None) -> dict | None:
    """Message timeline, exposure matrix, turn times and the idea uses of goal period g (non-holdout days)."""
    days = days if days is not None else sh.period_days(g)
    if not days:
        return None
    chat = sh.chat.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(days)).sort("msg")
    if chat.height == 0:
        return None
    rows = chat["msg"].to_numpy().astype(np.int64)
    pos = {int(r): i for i, r in enumerate(rows)}
    kind = chat["speaker_kind"].cast(pl.Utf8).replace_strict(KIND, default=3).to_numpy().astype(np.int8)
    sender = chat["agent"].fill_null(-1).to_numpy().astype(np.int16)
    hum = chat["human"].fill_null("").to_list()
    hcodes = {h: i for i, h in enumerate(sorted(set(hum) - {""}))}
    human = np.array([hcodes.get(h, -1) for h in hum], dtype=np.int32)
    day_idx = {d: i for i, d in enumerate(days)}
    t = _us(chat["t"])
    ex = sh.exposure.filter(pl.col("msg").is_in(rows))
    E = np.zeros((len(rows), sh.n_agents), dtype=bool)
    E[np.array([pos[int(m)] for m in ex["msg"].to_numpy()], dtype=np.int64), ex["agent"].to_numpy().astype(np.int64)] = True
    import datetime as dt
    t0 = chat["t"].min() - dt.timedelta(hours=8)
    t1 = chat["t"].max() + dt.timedelta(hours=1)
    turns = sh.turn_times(_EvShim(sh.ev), t0, t1)
    if uses is None:
        if ideas is None:
            ideas = sh.first_seen.filter(pl.col("first_goal") == g)["marker"].to_numpy()
        uses = sh.uses.filter(pl.col("msg").is_in(rows) & pl.col("marker").is_in(ideas))
    upos = np.array([pos[int(m)] for m in uses["msg"].to_numpy()], dtype=np.int64)
    out = dict(goal=g, days=days, rows=rows, t=t, kind=kind, sender=sender, human=human,
               day=np.array([day_idx[d] for d in chat["pt_date"].to_list()], dtype=np.int16),
               room=chat["room"].fill_null(-1).to_numpy().astype(np.int16), E=E, turns=turns, cc=sh.cc,
               use_pos=upos, use_marker=uses["marker"].to_numpy().astype(np.int64),
               use_cls=uses["cls"].to_numpy().astype(np.int8))
    if R1B:
        out.update(ledger_arrays(chat, t, kind, sender, sh.n_agents, t0, t1))
    return out


def ledger_arrays(chat: pl.DataFrame, t: np.ndarray, kind: np.ndarray, sender: np.ndarray, n_agents: int, t0, t1) -> dict:
    """Round 1b: TS[m, a] = t_call (us) of agent a's call that received message m (DQ1 context ledger; INF_US if never),
    and cs[m] = t_call of the call that produced agent message m (the sender's latest call with t_call < t_m)."""
    mids = chat["message_id"].to_list()
    pos = pl.DataFrame({"message_id": mids, "pos": np.arange(len(mids), dtype=np.int64)})
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id").join(
        pos.lazy(), on="message_id", how="inner").collect()
    cw = (pl.scan_parquet(SH / "call_windows.parquet").select("turn_id", "agent", "t_call", "holdout")
          .filter((pl.col("t_call") >= t0) & (pl.col("t_call") <= t1)).collect())
    assert not cw.filter(pl.col("turn_id").is_in(it["turn_id"].implode()))["holdout"].any(), "holdout call in a ledger join"
    j = it.join(cw.select("turn_id", "agent", "t_call"), on="turn_id", how="inner")
    TS = np.full((len(mids), n_agents), INF_US, dtype=np.int64)
    if j.height:
        np.minimum.at(TS, (j["pos"].to_numpy(), j["agent"].to_numpy().astype(np.int64)), _us(j["t_call"]))
    cs = t - GUARD_US
    cfb = np.ones(len(t), dtype=bool)
    for a in np.unique(sender[kind == 0]):
        if a < 0:
            continue
        ca = np.sort(_us(cw.filter(pl.col("agent") == int(a))["t_call"]))
        idx = np.where((kind == 0) & (sender == a))[0]
        if len(ca) == 0:
            continue
        k = np.searchsorted(ca, t[idx], side="left") - 1
        ok = k >= 0
        ok &= (t[idx] - ca[np.clip(k, 0, None)]) <= STALE_US
        cs[idx[ok]] = ca[k[ok]]
        cfb[idx[ok]] = False
    return dict(TS=TS, cs=cs, cs_fb=cfb, n_ledger_items=int(j.height))


# ------------------------------------------------------------------------------------------------ assembler
def call_starts(inp: dict) -> tuple[np.ndarray, np.ndarray]:
    """s[m] for every agent message m (H18 rule): latest turn of the sender before t_m - 1 s; else t_m - 1 s."""
    t, kind, sender = inp["t"], inp["kind"], inp["sender"]
    s = t - GUARD_US
    fb = np.ones(len(t), dtype=bool)
    for a in np.unique(sender[kind == 0]):
        idx = np.where((kind == 0) & (sender == a))[0]
        tt = inp["turns"].get(int(a))
        if tt is None or len(tt) == 0:
            continue
        j = np.searchsorted(tt, t[idx] - GUARD_US, side="left") - 1
        ok = j >= 0
        prev = np.where(ok, tt[np.clip(j, 0, None)], 0)
        ok &= (t[idx] - prev) <= STALE_US
        s[idx[ok]] = prev[ok]
        fb[idx[ok]] = False
    return s, fb


def _spk(kind, sender, human):
    """Speaker key: agents >= 0; humans -(1000 + code); automated -2."""
    out = sender.astype(np.int64).copy()
    out[kind == 1] = -(1000 + human[kind == 1].astype(np.int64))
    out[kind == 2] = -2
    out[kind == 3] = -3
    return out


def assemble(inp: dict, atrisk_cap: int = 4000, seed: int = 0, with_null: bool = True) -> dict:
    t, kind, sender = inp["t"], inp["kind"], inp["sender"]
    E, cc = inp["E"], inp["cc"]
    spk = _spk(kind, sender, inp["human"])
    if "TS" in inp:          # round 1b: ledger call starts and receipts
        s_all, fb_all, TS = inp["cs"], inp["cs_fb"], inp["TS"]
    else:
        s_all, fb_all = call_starts(inp)
        TS = None
    last_day = int(inp["day"].max())
    agents = sorted(int(a) for a in np.unique(sender[kind == 0]) if int(a) >= 0 and int(a) not in cc)
    talk = {a: np.where((kind == 0) & (sender == a))[0] for a in agents}
    talk_t = {a: t[p] for a, p in talk.items()}
    talk_s = {a: s_all[p] for a, p in talk.items()}
    # group uses by idea
    order = np.lexsort((inp["use_pos"], inp["use_marker"]))
    um, up, uc = inp["use_marker"][order], inp["use_pos"][order], inp["use_cls"][order]
    brk = np.r_[0, np.where(np.diff(um) != 0)[0] + 1, len(um)]
    rng = np.random.default_rng(seed)
    idea_ids = um[brk[:-1]]
    idea_cls = uc[brk[:-1]]
    # at-risk subsample (per class cap), fixed seed
    ar_set = set()
    for c in np.unique(idea_cls):
        ids = idea_ids[idea_cls == c]
        pick = ids if len(ids) <= atrisk_cap else rng.choice(ids, atrisk_cap, replace=False)
        ar_set.update(int(x) for x in pick)
    FU, TR, AR, JT, RX = [], [], [], [], []
    for b in range(len(brk) - 1):
        lo, hi = brk[b], brk[b + 1]
        mk, cl = int(um[lo]), int(uc[lo])
        P = up[lo:hi]                                   # use positions, time-sorted (msgs are sorted by t)
        Pt, Pk, Ps = t[P], kind[P], spk[P]
        first_pos = int(P[0])
        # first use per agent (non-cc)
        fu = {}
        for p, k_, sp in zip(P, Pk, Ps):
            if k_ == 0 and sp >= 0 and int(sp) not in cc and int(sp) not in fu:
                fu[int(sp)] = int(p)
        nodes = sorted(fu.items(), key=lambda kv: kv[1])
        node_of = {}
        rows_idea = []
        for a, u in nodes:
            if u == first_pos:
                st, par_r, par_e, ksrc, nexp, lag, fvis = 0, -9, -9, 0, 0, 0, -1
            else:
                su = s_all[u]
                vis = ((TS[P, a] <= su) if TS is not None else ((Pt < su) & E[P, a])) & (Ps != a)
                if vis.any():
                    vi = np.where(vis)[0]
                    st = 1
                    par_r, par_e = int(Ps[vi[-1]]), int(Ps[vi[0]])
                    ksrc, nexp = len(set(Ps[vi].tolist())), len(vi)
                    ts = talk_s[a]
                    if TS is not None:
                        fvis = int(TS[P[vi], a].min())
                        lag = int(np.sum((ts >= fvis) & (talk[a] <= u)))
                    else:
                        fvis = int(Pt[vi[0]])
                        lag = int(np.sum((ts > fvis) & (talk[a] <= u)))
                else:
                    st, par_r, par_e, ksrc, nexp, lag, fvis = 2, -9, -9, 0, 0, 0, -1
            rows_idea.append([a, u, st, par_r, par_e, ksrc, nexp, lag])
            node_of[a] = len(rows_idea) - 1
        # trees
        n = len(rows_idea)
        root = np.arange(n)
        gen = np.zeros(n, dtype=np.int16)
        rtype = np.full(n, -1, dtype=np.int8)
        par_node = np.full(n, -1, dtype=np.int32)
        for i, r in enumerate(rows_idea):
            st, pr = r[2], r[3]
            if st == 1 and pr >= 0 and pr in node_of and node_of[pr] < i:
                pn = node_of[pr]
                par_node[i] = pn
                root[i] = root[pn]
                gen[i] = gen[pn] + 1
            else:
                rtype[i] = 0 if st == 0 else (2 if st == 2 else 1)
        offs = np.bincount(par_node[par_node >= 0], minlength=n) if n else np.zeros(0, int)
        for i, r in enumerate(rows_idea):
            a, u, st, pr, pe, ksrc, nexp, lag = r
            FU.append((mk, cl, a, u, t[u], st, pr, pe, ksrc, nexp, lag, int(root[i]), int(gen[i]), int(offs[i]),
                       bool(fb_all[u]), int(inp["day"][u])))
        for ri in np.unique(root) if n else []:
            members = np.where(root == ri)[0]
            u0 = rows_idea[ri][1]
            TR.append((mk, cl, int(ri), rows_idea[ri][0], int(rtype[ri]), len(members), int(gen[members].max()),
                       int(inp["day"][u0]) == last_day, int(inp["day"][u0]), int(t[u0])))
        # ------------------------------------------------ jitter null (per non-seed agent first use)
        if with_null:
            for a, u, st, *_ in rows_idea:
                if st == 0:
                    continue
                other = Ps != a
                tfo = Pt[other].min() if other.any() else Pt[0]
                ta, sa, pa = talk_t[a], talk_s[a], talk[a]
                if TS is not None:
                    vt = np.sort(TS[P[other], a]); vt = vt[vt < INF_US]
                else:
                    visa = other & E[P, a]
                    vt = Pt[visa]
                after = ta > tfo
                exp_turn = np.zeros(len(ta), dtype=bool)
                if len(vt):
                    exp_turn = np.searchsorted(vt, sa, side="right" if TS is not None else "left") > 0
                first_exp = np.zeros(len(ta), dtype=bool)
                ii = np.where(exp_turn & after)[0]
                if len(ii):
                    first_exp[ii[0]] = True
                tu = t[u]
                obs_exp = st == 1
                k_u = int(np.where(pa == u)[0][0]) if (pa == u).any() else -1
                obs_first = bool(k_u >= 0 and first_exp[k_u])
                rec = [mk, cl, a, u, obs_exp, obs_first]
                for D in DELTAS_S:
                    cand = after & (np.abs(ta - tu) <= D * US)
                    nc = int(cand.sum())
                    rec += [float(exp_turn[cand].mean()) if nc else float(obs_exp), nc]
                cand = after & (np.abs(ta - tu) <= 3600 * US)
                rec.append(float(first_exp[cand].mean()) if cand.any() else float(obs_first))
                JT.append(tuple(rec))
        # ------------------------------------------------ at-risk turns (dose response), subsample
        if mk in ar_set:
            t_first = Pt[0]
            for a in agents:
                if a in fu and fu[a] == first_pos:
                    continue
                ta, sa, pa = talk_t[a], talk_s[a], talk[a]
                sel = ta > t_first
                if a in fu:
                    sel &= pa <= fu[a]
                if not sel.any():
                    continue
                idx = np.where(sel)[0]
                if TS is not None:
                    oth = Ps != a
                    tsv = TS[P[oth], a]
                    okv = tsv < INF_US
                    oo = np.argsort(tsv[okv], kind="stable")
                    vt, vs = tsv[okv][oo], Ps[oth][okv][oo]
                    side = "right"
                    # H57 placebo flags: another agent's use posted within RECENT_US before the talk, read (TS <= call
                    # start) vs not yet read (TS > call start, eventually received: same room, in flight)
                    pt_o, ts_o = Pt[oth][okv], tsv[okv]
                    sr = np.zeros(len(idx), dtype=bool); ur = np.zeros(len(idx), dtype=bool)
                    lo_w = np.searchsorted(pt_o, ta[idx] - RECENT_US, side="left")
                    hi_w = np.searchsorted(pt_o, ta[idx], side="left")
                    for q in np.flatnonzero(hi_w > lo_w):
                        tw_ = ts_o[lo_w[q]:hi_w[q]]
                        sr[q] = bool(tw_.min() <= sa[idx][q]); ur[q] = bool(tw_.max() > sa[idx][q])
                else:
                    visa = (Ps != a) & E[P, a]
                    vt, vs = Pt[visa], Ps[visa]
                    side = "left"
                    sr = ur = np.zeros(len(idx), dtype=bool)
                kr = np.zeros(len(idx), dtype=np.int16)
                if len(vt):
                    cnt = np.searchsorted(vt, sa[idx], side=side)
                    seen, cd = set(), np.zeros(len(vt) + 1, dtype=np.int16)
                    for q, x in enumerate(vs):
                        seen.add(int(x))
                        cd[q + 1] = len(seen)
                    ks = cd[cnt]
                    # recency window: sources whose use arrived within the agent's last MEM_TURNS call windows
                    s_back = np.r_[np.full(MEM_TURNS, np.iinfo(np.int64).min), sa][: len(sa)][idx]
                    lo_r = np.searchsorted(vt, s_back, side=side)
                    for q in range(len(idx)):
                        if cnt[q] > lo_r[q]:
                            kr[q] = len(set(vs[lo_r[q]:cnt[q]].tolist()))
                else:
                    ks = np.zeros(len(idx), dtype=np.int16)
                adopt = (pa[idx] == fu[a]) if a in fu else np.zeros(len(idx), dtype=bool)
                exp_i = np.where(ks > 0)[0]
                keep = np.zeros(len(idx), dtype=bool)
                keep[(ks == 0) & (ta[idx] - t_first <= DAY_US)] = True
                tsince = np.zeros(len(idx), dtype=np.int16)
                if len(exp_i):
                    e0 = exp_i[0]
                    keep[e0:e0 + H_TURNS] |= ks[e0:e0 + H_TURNS] > 0
                    tsince[e0:] = np.arange(1, len(idx) - e0 + 1)
                for q in np.where(keep)[0]:
                    kb = min(int(ks[q]), 3)
                    tb = 0 if kb == 0 else (1 if tsince[q] == 1 else 2 if tsince[q] == 2 else 3 if tsince[q] <= 5 else 4)
                    AR.append((mk, cl, kb, min(int(kr[q]), 3), tb, bool(adopt[q]), bool(sr[q]), bool(ur[q])))
            # ------------------------------------------------ 24 h exposed vs never-exposed contrast
            t_end = t_first + DAY_US
            win = (Pt >= t_first) & (Pt < t_end)
            ne = na = ue = ua = 0
            for a in agents:
                if a in fu and fu[a] == first_pos:
                    continue
                ta, sa = talk_t[a], talk_s[a]
                w = (ta > t_first) & (ta < t_end)
                if not w.any():
                    continue
                if TS is not None:
                    tw = TS[P[win & (Ps != a)], a]
                    exposed = bool(len(tw) and tw.min() <= sa[w].max())
                else:
                    visa = win & (Ps != a) & E[P, a]
                    exposed = bool(visa.any() and Pt[visa].min() < sa[w].max())
                adopted = a in fu and t[fu[a]] < t_end
                if exposed:
                    ne += 1
                    na += adopted
                else:
                    ue += 1
                    ua += adopted
            RX.append((mk, cl, ne, na, ue, ua, int(Pk[0])))
    fu_cols = ["idea", "cls", "agent", "pos", "t_us", "status", "parent", "parent_earliest", "k_src", "n_exp", "lag_turns",
               "tree", "gen", "offspring", "s_fallback", "day"]
    tr_cols = ["idea", "cls", "tree", "root_agent", "root_type", "size", "depth", "censored", "day", "t_us"]
    jt_cols = ["idea", "cls", "agent", "pos", "obs_exposed", "obs_first_turn", "p_exp_30m", "n_c30m", "p_exp_1h", "n_c1h",
               "p_exp_2h", "n_c2h", "p_first_1h"]
    ar_cols = ["idea", "cls", "kbin", "krbin", "tbin", "adopt", "sr", "ur"]
    rx_cols = ["idea", "cls", "n_exposed", "n_exposed_adopt", "n_unexposed", "n_unexposed_adopt", "first_kind"]
    out = {
        "first_uses": pl.DataFrame(FU, schema=fu_cols, orient="row"),
        "trees": pl.DataFrame(TR, schema=tr_cols, orient="row"),
        "jitter": pl.DataFrame(JT, schema=jt_cols, orient="row"),
        "roomx": pl.DataFrame(RX, schema=rx_cols, orient="row"),
    }
    ar = pl.DataFrame(AR, schema=ar_cols, orient="row")
    if TS is None:      # round 1: same table as before (no H57 placebo flags)
        ar = ar.drop("sr", "ur")
    gk = ["idea", "cls", "kbin", "krbin", "tbin"] + (["sr", "ur"] if TS is not None else [])
    out["atrisk"] = (ar.group_by(gk).agg(pl.len().alias("turns"), pl.col("adopt").sum().alias("adopts"))
                     .sort(gk) if ar.height else
                     pl.DataFrame(schema={"idea": pl.Int64, "cls": pl.Int8, "kbin": pl.Int64, "krbin": pl.Int64, "tbin": pl.Int64,
                                          **({"sr": pl.Boolean, "ur": pl.Boolean} if TS is not None else {}),
                                          "turns": pl.UInt32, "adopts": pl.UInt32}))
    out["meta"] = dict(visibility="ledger" if TS is not None else "h18_call_start", n_ledger_items=int(inp.get("n_ledger_items", -1)),
                       n_msgs=len(t), n_agent_msgs=int((kind == 0).sum()), n_agents=len(agents),
                       n_ideas=int(len(idea_ids)), s_fallback_frac=float(fb_all[kind == 0].mean()) if (kind == 0).any() else 0.0,
                       n_rooms_active=int(len(np.unique(inp["room"][kind == 0]))), last_day=last_day,
                       n_days=len(inp["days"]))
    return out
