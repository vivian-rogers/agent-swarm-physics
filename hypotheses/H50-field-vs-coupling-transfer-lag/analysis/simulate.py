"""Synthetic swarms for H50 (axis F): a gated kinetic swarm at village sampling.

Each agent runs a call loop. At a call's context-assembly time it reads the room items posted since its previous
call (gated) or up to the end of its own call (ungated rival R2). Items carry effects on the logits of the call
outcomes (talk; pause vs act), applied from hop 1+dead onward with a geometric decay over hops. A slow
Ornstein-Uhlenbeck field z(t) shared by all agents (unmeasured common drive) and a day-edge boost (measured via
the resume input) add common drive. Real input schedules (bookends, human messages, nudges) are replayed.

Output: a unit dict in h50lib's format plus ground truth (per-pair marginal effects at the read-out call).
"""
from __future__ import annotations

import heapq

import numpy as np

import h50lib as L


DEFAULT = dict(
    N=10, rooms=None,                 # rooms[i] (default all 0)
    busy_med=11.0, busy_sig=0.6,      # act-call duration (s), lognormal
    talk_extra=8.0,                   # extra seconds for a talk call
    overhead=1.7,                     # scaffold overhead between chained calls
    cadence=None,                     # regime-I chat mode: scheduled start-to-start cadence (s, lognormal median) or None
    cad_sig=0.35,
    pause_med=180.0, pause_sig=0.9, pause_wake=3.2,
    a_talk=-3.0, a_pause=-2.6,        # baseline logits (talk among act calls; pause)
    edge_amp=0.0, edge_tau=900.0,     # day-start boost on talk and act logits (measured field via the edge input)
    g_talk=None, g_act=None,          # dict kind -> (target amp, bystander amp) on logits
    dead_f=0,                         # field dead time (hops)
    J_talk=0.0, J_act=0.0, dead_c=0,  # peer coupling per item (logit), dead time in hops
    tau_h=1.5,                        # decay of item effects over hops (e-folding in hops)
    nhop_eff=8,
    ou_sig=0.0, ou_tau=900.0,         # unmeasured common field
    ungated=False,
    start_med=20.0,                   # scaffold start delay after the day start (s)
)


def _ou(rng, t0, t1, sig, tau, dt=10.0):
    n = int((t1 - t0) / dt) + 2
    z = np.zeros(n)
    a = np.exp(-dt / tau)
    b = sig * np.sqrt(1 - a * a)
    z[0] = rng.normal(0, sig)
    for k in range(1, n):
        z[k] = a * z[k - 1] + b * rng.normal()
    return z, dt


def simulate(sched, prm, seed=0):
    """sched: dict(days=[(t0, t1)], inputs=[(t, kind, room, targets tuple)]) with t in seconds; t0/t1 the calendar
    window. Returns (unit, truth)."""
    p = dict(DEFAULT)
    p.update(prm)
    rng = np.random.default_rng(seed)
    N = p["N"]
    rooms = np.zeros(N, int) if p["rooms"] is None else np.asarray(p["rooms"])
    g_talk = p["g_talk"] or {}
    g_act = p["g_act"] or {}
    dec = np.exp(-np.arange(p["nhop_eff"]) / p["tau_h"])
    calls = {k: [] for k in ("agent", "day", "tc", "tl", "talk", "act", "first", "low")}
    msgs = {k: [] for k in ("t", "day", "sender", "room")}
    mp_msg, mp_rec = [], []
    truth_pairs = []            # (msg idx, recipient, marginal effect on P(talk) at read-out call, read-out tc)
    for d, (t0, t1) in enumerate(sched["days"]):
        z, zdt = _ou(rng, t0 - 600, t1 + 600, p["ou_sig"], p["ou_tau"]) if p["ou_sig"] > 0 else (None, None)

        def zf(t):
            return 0.0 if z is None else z[int((t - t0 + 600) / zdt)]
        # room post lists (time-ordered as posted): (t, kind, sender, room, targets, msg_idx)
        posts = []
        ev = []
        seq = 0
        for (t, kind, room, tg) in sched["inputs"]:
            if t0 - 900 <= t <= t1:
                heapq.heappush(ev, (t, seq, "post", (kind, -1, room, tuple(tg), -1)))
                seq += 1
        last_vis = np.full(N, t0 - 900.0)
        ptr = np.zeros(N, int)            # index into posts already read
        eff_t = np.zeros((N, p["nhop_eff"] + 8))
        eff_a = np.zeros((N, p["nhop_eff"] + 8))
        effp_t = np.zeros((N, p["nhop_eff"] + 8))   # peer-only part (truth)
        first = np.ones(N, bool)
        tracked = [[] for _ in range(N)]
        for i in range(N):
            ts = t0 + rng.lognormal(np.log(p["start_med"]), 0.5)
            heapq.heappush(ev, (ts, seq, "start", (i,)))
            seq += 1
        while ev:
            t, _, typ, data = heapq.heappop(ev)
            if typ == "post":
                kind, sender, room, tg, midx = data
                posts.append((t, kind, sender, room, tg, midx))
                continue
            if typ == "start":
                (i,) = data
                if t > t1:
                    continue
                dur = rng.lognormal(np.log(p["busy_med"]), p["busy_sig"])
                tvis = t + dur if p["ungated"] else t
                heapq.heappush(ev, (tvis, seq, "decide", (i, t, dur)))
                seq += 1
                continue
            # decide: read items posted in [last_vis, tvis)
            i, tc, dur = data
            tvis = t
            new_items = []
            while ptr[i] < len(posts) and posts[ptr[i]][0] < tvis:
                it = posts[ptr[i]]
                ptr[i] += 1
                if it[0] < last_vis[i] or (it[3] >= 0 and it[3] != rooms[i]) or it[2] == i:
                    continue
                new_items.append(it)
            last_vis[i] = tvis
            peer_read = []
            for (tm, kind, sender, room, tg, midx) in new_items:
                if kind == "peer":
                    k0 = p["dead_c"]   # effect at the read-out call itself is hop 1 = index 0 here
                    n = p["nhop_eff"]
                    eff_t[i, k0:k0 + n] += p["J_talk"] * dec
                    eff_a[i, k0:k0 + n] += p["J_act"] * dec
                    effp_t[i, k0:k0 + n] += p["J_talk"] * dec
                    peer_read.append(midx)
                else:
                    tgt = i in tg
                    at = g_talk.get(kind, (0.0, 0.0))[0 if tgt else 1]
                    aa = g_act.get(kind, (0.0, 0.0))[0 if tgt else 1]
                    k0 = p["dead_f"]
                    n = p["nhop_eff"]
                    eff_t[i, k0:k0 + n] += at * dec
                    eff_a[i, k0:k0 + n] += aa * dec
            edge = p["edge_amp"] * np.exp(-max(tc - t0, 0) / p["edge_tau"])
            zz = zf(tvis)
            Ha = p["a_pause"] - eff_a[i, 0] - edge - zz
            p_pause = 1 / (1 + np.exp(-Ha))
            Ht = p["a_talk"] + eff_t[i, 0] + edge + zz
            p_talk = 1 / (1 + np.exp(-Ht))
            # truth: marginal effect of each tracked peer item on P(talk call) at hops 1..6 after its read-out
            tracked[i] = [(mi, h + 1) for (mi, h) in tracked[i] if h + 1 <= 6] + [(mi, 1) for mi in peer_read]
            for (mi, h) in tracked[i]:
                q = h - 1 - p["dead_c"]
                at = p["J_talk"] * dec[q] if 0 <= q < len(dec) else 0.0
                aa = p["J_act"] * dec[q] if 0 <= q < len(dec) else 0.0
                p0 = 1 / (1 + np.exp(-(Ht - at)))
                pa0 = 1 / (1 + np.exp(-(Ha + aa)))
                truth_pairs.append((mi, i, (1 - p_pause) * p_talk - (1 - pa0) * p0, tc, h))
            is_pause = rng.random() < p_pause
            is_talk = (not is_pause) and (rng.random() < p_talk)
            # shift effect arrays by one hop (this call consumed hop index 0)
            eff_t[i, :-1] = eff_t[i, 1:]
            eff_t[i, -1] = 0
            eff_a[i, :-1] = eff_a[i, 1:]
            eff_a[i, -1] = 0
            effp_t[i, :-1] = effp_t[i, 1:]
            effp_t[i, -1] = 0
            if is_talk:
                dur += p["talk_extra"]
            tl = tc if is_pause else tc + dur
            calls["agent"].append(i)
            calls["day"].append(d)
            calls["tc"].append(tc)
            calls["tl"].append(tl)
            calls["talk"].append(is_talk)
            calls["act"].append(not is_pause)
            calls["first"].append(bool(first[i]))
            calls["low"].append(False)
            first[i] = False
            if is_talk:
                midx = len(msgs["t"])
                msgs["t"].append(tc + dur)
                msgs["day"].append(d)
                msgs["sender"].append(i)
                msgs["room"].append(rooms[i])
                heapq.heappush(ev, (tc + dur, seq, "post", ("peer", i, rooms[i], (), midx)))
                seq += 1
            # next call
            if is_pause:
                nxt = tc + rng.lognormal(np.log(p["pause_med"]), p["pause_sig"]) + p["pause_wake"]
            elif p["cadence"]:
                nxt = tc + max(rng.lognormal(np.log(p["cadence"]), p["cad_sig"]), dur + 2)
            else:
                nxt = tc + dur + p["overhead"]
            if nxt < t1:
                heapq.heappush(ev, (nxt, seq, "start", (i,)))
                seq += 1
        # visibility pairs for this day's peer messages: everyone else in the room
    msgs = {k: np.asarray(v) for k, v in msgs.items()}
    for m in range(len(msgs["t"])):
        for j in range(N):
            if j != msgs["sender"][m] and rooms[j] == msgs["room"][m]:
                mp_msg.append(m)
                mp_rec.append(j)
    c = {k: np.asarray(v) for k, v in calls.items()}
    o = np.lexsort((c["tc"], c["agent"]))
    c = {k: v[o] for k, v in c.items()}
    c["agent"] = c["agent"].astype(np.int64)
    c["day"] = c["day"].astype(np.int64)
    # inputs
    kinds, it, iday, tg = [], [], [], []
    ipi, ipr, ipt = [], [], []
    for (t, kind, room, targets) in sched["inputs"]:
        for d, (t0, t1) in enumerate(sched["days"]):
            if t0 - 900 <= t <= t1:
                k = len(it)
                it.append(t)
                iday.append(d)
                kinds.append(L.K[kind])
                for j in range(N):
                    if rooms[j] == room or room < 0:
                        ipi.append(k)
                        ipr.append(j)
                        ipt.append(j in targets)
    U = dict(name="synthetic", regime="syn", N=N,
             day_t0=np.array([a - 900 for a, b in sched["days"]], float),
             day_t1=np.array([b + 300 for a, b in sched["days"]], float),
             calls=c,
             msgs=dict(t=msgs["t"].astype(float), day=msgs["day"].astype(np.int64),
                       sender=msgs["sender"].astype(np.int64), room=msgs["room"].astype(np.int64)),
             mpairs=dict(msg=np.asarray(mp_msg, np.int64), rec=np.asarray(mp_rec, np.int64)),
             inputs=dict(t=np.asarray(it, float), day=np.asarray(iday, np.int64), kind=np.asarray(kinds, np.int64)),
             ipairs=dict(inp=np.asarray(ipi, np.int64), rec=np.asarray(ipr, np.int64), tgt=np.asarray(ipt, bool)),
             plat=dict(t=np.zeros(0), day=np.zeros(0, np.int64), agent=np.zeros(0, np.int64)))
    tp = np.array(truth_pairs, float) if truth_pairs else np.zeros((0, 5))
    return U, dict(pairs=tp)
