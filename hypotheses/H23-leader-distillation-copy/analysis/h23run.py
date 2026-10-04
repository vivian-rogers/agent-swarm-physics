"""H23 period analysis: observables O1-O3 and the rival tests for one goal period (G44 exploratory; #45 confirmatory).

`run_period(pdir, cfg)` reads, from data/processed/H23-leader-distillation-copy/:
    G44/corpus_text.parquet, G44/corpus_emb.npz, G44/offline_text.parquet   (the corpus is the same for every period)
    <pdir>/messages.parquet, <pdir>/vectors.npz                              (scheme/build_messages.py)
and shared chat_text for message text. It writes <pdir>/results.json and <pdir>/features.parquet (no text).

Groups (cfg): leader = live messages of the leader agents with checkpoint in cfg['checkpoints'];
K_same / V_same = Kimi K2.6 / other agents' live messages in the same room and window; CTRL = K_same + V_same;
K_field = Kimi K2.6 in the base-field periods (live window excluded); C = recovered v7-aug-64 targets.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h23lib as L  # noqa: E402
from common import load_whitener  # noqa: E402

G44 = L.OUT / "G44"
RNG_SEED = 20261003


def _texts(ids: list[str]) -> dict:
    t = pl.read_parquet(L.SH / "chat_text.parquet", columns=["message_id", "text"]).filter(
        pl.col("message_id").is_in(ids))
    return dict(zip(t["message_id"].to_list(), t["text"].to_list()))


def _boot_ci(vals: np.ndarray, fn=np.mean, n=2000, seed=0):
    vals = np.asarray(vals, float)
    vals = vals[~np.isnan(vals)]
    rng = np.random.default_rng(seed)
    bs = [fn(rng.choice(vals, len(vals))) for _ in range(n)]
    return [float(fn(vals)), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def _share(primaries, acts=L.DIRECTIVE):
    return float(np.mean([p in acts for p in primaries])) if len(primaries) else float("nan")


def run_period(pdir: Path, cfg: dict) -> dict:
    M = pl.read_parquet(pdir / "messages.parquet")
    V = np.load(pdir / "vectors.npz", allow_pickle=False)
    zpos = {(m, s): i for i, (m, s) in enumerate(zip(V["message_id"], V["set"]))}
    Z, Zc = V["z"], V["z_ctx"]
    W = load_whitener("III", 32)

    per = M.filter(pl.col("set") == "period")
    lead = per.filter((pl.col("group") == "leader") & pl.col("live") & pl.col("checkpoint").is_in(cfg["checkpoints"]))
    ksame = per.filter((pl.col("group") == "kimi") & pl.col("live"))
    vsame = per.filter((pl.col("group") == "village") & pl.col("live"))
    ctrl = pl.concat([ksame, vsame])
    kfield = M.filter(pl.col("set") == "field")
    bg = M.filter(pl.col("set") == "background")
    C = pl.read_parquet(G44 / "corpus_text.parquet")
    if not cfg.get("corpus_unplaced", False):
        C = C.filter(pl.col("member"))
    CE = np.load(G44 / "corpus_emb.npz")
    cmask = np.array(pl.read_parquet(G44 / "corpus_text.parquet")["member"].to_list()) if not cfg.get(
        "corpus_unplaced", False) else np.ones(len(CE["target"]), bool)
    zC = W(CE["target"][cmask])
    zS = W(CE["snippet"][cmask])
    off = pl.read_parquet(G44 / "offline_text.parquet")
    zO = W(CE["offline"])

    ids = list(set(per["message_id"].to_list() + kfield["message_id"].to_list() + bg["message_id"].to_list()))
    T = _texts(ids)
    txt = lambda df: [T.get(m) or "" for m in df["message_id"].to_list()]
    c_txt = C["response"].to_list()
    groups = {"leader": lead, "K_same": ksame, "V_same": vsame, "CTRL": ctrl}
    R: dict = {"n": {k: v.height for k, v in groups.items()} | {"K_field": kfield.height, "corpus": C.height,
                                                                "offline": off.height}}

    # ------------------------------------------------------------------ O1 phrase level
    cs = {1: set(), 2: set(), 3: set()}
    for s in c_txt:
        tok = L.tokens(s)
        cs[1] |= L.ngram_set(tok, 1, content_only=True)
        cs[2] |= L.ngram_set(tok, 2)
        cs[3] |= L.ngram_set(tok, 3)
    prior = L.ngram_counts(txt(bg), 1) + L.ngram_counts(txt(bg), 2)
    cC = L.ngram_counts(c_txt, 1) + L.ngram_counts(c_txt, 2)
    cK = L.ngram_counts(txt(kfield), 1) + L.ngram_counts(txt(kfield), 2)
    z = L.log_odds_z(cC, cK, prior, a0=1000.0)
    mk_c = {w for w, v in z.items() if v >= 1.96 and cC.get(w, 0) >= 2}
    mk_k = {w for w, v in z.items() if v <= -1.96 and cK.get(w, 0) >= 2}
    split = lambda S: ({w for w in S if isinstance(w, str)}, {w for w in S if isinstance(w, tuple)})
    mc1, mc2 = split(mk_c)
    mb1, mb2 = split(mk_k)
    R["markers"] = {"corpus_distinctive": len(mk_c), "corpus_uni": len(mc1), "corpus_bi": len(mc2),
                    "base_distinctive": len(mk_k),
                    "corpus_marker_classes": dict(Counter(_marker_class(w) for w in mk_c)),
                    "base_marker_classes": dict(Counter(_marker_class(w) for w in mk_k))}

    def lex(df, texts=None):
        texts = texts if texts is not None else txt(df)
        return {
            "c1": np.array([L.copy_fraction(s, cs[1], 1, True) for s in texts]),
            "c2": np.array([L.copy_fraction(s, cs[2], 2) for s in texts]),
            "c3": np.array([L.copy_fraction(s, cs[3], 3) for s in texts]),
            "r_corpus": np.array([L.marker_rate(s, mc1, mc2) for s in texts]),
            "r_base": np.array([L.marker_rate(s, mb1, mb2) for s in texts]),
            "ntok": np.array([len(L.tokens(s)) for s in texts]),
        }
    LX = {k: lex(v) for k, v in groups.items()}
    LX["K_field"] = lex(kfield)
    LX["offline"] = lex(None, off["response"].to_list())
    # corpus self-copy (leave-one-out) as the ceiling for c^(n)
    loo = {n: [] for n in (1, 2, 3)}
    for i, s in enumerate(c_txt):
        rest = [c_txt[j] for j in range(len(c_txt)) if j != i]
        ref = {1: set(), 2: set(), 3: set()}
        for r in rest:
            tok = L.tokens(r)
            ref[1] |= L.ngram_set(tok, 1, True)
            ref[2] |= L.ngram_set(tok, 2)
            ref[3] |= L.ngram_set(tok, 3)
        for n in (1, 2, 3):
            loo[n].append(L.copy_fraction(s, ref[n], n, n == 1))
    R["O1"] = {"means": {g: {k: _boot_ci(v) for k, v in d.items() if k != "ntok"} for g, d in LX.items()},
               "corpus_loo": {f"c{n}": _boot_ci(np.array(loo[n])) for n in (1, 2, 3)}}
    tests = {}
    for stat in ("c1", "c2", "c3", "r_corpus"):
        for other in ("CTRL", "K_same", "V_same", "K_field"):
            tests[f"{stat}:leader>{other}"] = L.perm_mean_diff(LX["leader"][stat], LX[other][stat], seed=RNG_SEED)
    for other in ("CTRL", "K_same", "K_field"):
        tests[f"r_base:leader<{other}"] = L.perm_mean_diff(LX[other]["r_base"], LX["leader"]["r_base"], seed=RNG_SEED)
    R["O1"]["tests"] = tests

    # pooled lexical copy information d(a||b): token-level n-gram occurrences inside the corpus set
    def pooled(texts, n):
        hit = tot = 0
        for s in texts:
            tok = L.tokens(s)
            grams = [t for t in tok if t not in L.STOP and len(t) > 2] if n == 1 else \
                [tuple(tok[i:i + n]) for i in range(len(tok) - n + 1)]
            hit += sum(g in cs[n] for g in grams)
            tot += len(grams)
        return hit, tot
    R["O1"]["copy_information"] = {}
    for n in (1, 2, 3):
        ha, ta = pooled(txt(lead), n)
        hb, tb = pooled(txt(ctrl), n)
        hk, tk = pooled(txt(kfield), n)
        a, b, bk = ha / max(ta, 1), hb / max(tb, 1), hk / max(tk, 1)
        rng = np.random.default_rng(RNG_SEED)
        lt, ct = txt(lead), txt(ctrl)
        bs = []
        for _ in range(1000):
            h1, t1 = pooled([lt[i] for i in rng.integers(0, len(lt), len(lt))], n) if lt else (0, 1)
            h2, t2 = pooled([ct[i] for i in rng.integers(0, len(ct), len(ct))], n) if ct else (0, 1)
            aa, bb = h1 / max(t1, 1), h2 / max(t2, 1)
            bs.append(L.binary_kl(aa, bb) if aa > bb else 0.0)
        R["O1"]["copy_information"][f"n{n}"] = {
            "a_leader": a, "b_ctrl": b, "b_kfield": bk,
            "I_copy_bits_vs_ctrl": L.binary_kl(a, b) if a > b else 0.0,
            "I_copy_bits_vs_kfield": L.binary_kl(a, bk) if a > bk else 0.0,
            "I_copy_vs_ctrl_ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
            "P_I_copy_zero": float(np.mean(np.array(bs) == 0))}

    # ------------------------------------------------------------------ O2 plan level
    cprim = [L.plan_acts(s)["primary"] for s in c_txt]
    oprim = [L.plan_acts(s)["primary"] for s in off["response"].to_list()]
    prof = {"leader": lead["primary"].to_list(), "corpus": cprim, "K_same": ksame["primary"].to_list(),
            "V_same": vsame["primary"].to_list(), "CTRL": ctrl["primary"].to_list(),
            "K_field": kfield["primary"].to_list(), "leader_ctx": [p for p in lead["prev_act"].to_list() if p],
            "offline": oprim}
    R["O2"] = {"profiles": {g: dict(Counter(v)) for g, v in prof.items()},
               "directive_share": {g: _boot_ci(np.array([p in L.DIRECTIVE for p in v], float)) if v else None
                                   for g, v in prof.items()}}
    pc = L.profile(cprim, 0.5)
    R["O2"]["jsd"] = {g: L.jsd(L.profile(v, 0.5), pc) for g, v in prof.items() if v and g != "corpus"}
    R["O2"]["jsd_leader"] = {g: L.jsd(L.profile(prof["leader"], 0.5), L.profile(v, 0.5))
                             for g, v in prof.items() if v and g != "leader"}
    rng = np.random.default_rng(RNG_SEED)
    nl = max(len(prof["leader"]), 1)
    selfj = [L.jsd(L.profile(list(rng.choice(cprim, nl)), 0.5), pc) for _ in range(5000)]
    R["O2"]["jsd_corpus_self_n"] = {"n": nl, "p95": float(np.percentile(selfj, 95)), "mean": float(np.mean(selfj))}
    # coarse shares
    R["O2"]["coarse"] = {g: dict(Counter(L.COARSE[p] for p in v)) for g, v in prof.items()}

    # O2b corpus -> speaker channel, nearest-snippet pairing (k = 3), for leader and each control group
    cact = np.array([L.ACTS.index(p) for p in cprim])
    cco = np.array([L.COARSE_ACTS.index(L.COARSE[p]) for p in cprim])
    sn = zS / np.linalg.norm(zS, axis=1, keepdims=True)
    within = np.array([np.sort(sn[i] @ np.delete(sn, i, 0).T)[-1] for i in range(len(sn))])
    R["O2"]["snippet_within_top1"] = _boot_ci(within)

    def channel(df, kk=3):
        ix = [zpos[(m, "period")] for m in df["message_id"].to_list()]
        zc = Zc[ix]
        ok = ~np.isnan(zc).any(1)
        zc = zc[ok]
        sims = (zc / np.linalg.norm(zc, axis=1, keepdims=True)) @ sn.T
        top = np.argsort(-sims, axis=1)[:, :kk]
        out = {"n": int(ok.sum()), "top1_sim": _boot_ci(np.sort(sims, axis=1)[:, -1])}
        prim = np.array(df["primary"].to_list())[ok]
        for name, codes, acts in (("fine", cact, L.ACTS), ("coarse", cco, L.COARSE_ACTS)):
            k = len(acts)
            P = np.zeros((len(top), k))
            for m, row in enumerate(top):
                for j in row:
                    P[m, codes[j]] += 1.0 / kk
            P = (P + 0.1 / k) / (1 + 0.1)
            y = np.array([acts.index(p if name == "fine" else L.COARSE[p]) for p in prim])
            if len(y) < 3:
                out[name] = None
                continue
            res = L.soft_channel_test(P, y, k, n_null=2000, seed=RNG_SEED)
            # perfect-copy reference: the speaker draws its act from the paired corpus distribution itself
            rr = np.random.default_rng(RNG_SEED + 1)
            ref = []
            for _ in range(200):
                yc = np.array([rr.choice(k, p=P[m] / P[m].sum()) for m in range(len(y))])
                t = L.soft_channel_test(P, yc, k, n_null=200, seed=int(rr.integers(1e9)))
                ref.append([t["c_ex"], t["I_copy_ex"], t["I_transform_ex"]])
            ref = np.array(ref)
            res["perfect_copy_ref"] = {"c_ex": float(ref[:, 0].mean()), "I_copy_ex": float(ref[:, 1].mean()),
                                       "I_transform_ex": float(ref[:, 2].mean())}
            res["copy_efficiency"] = (res["c_ex"] / ref[:, 0].mean()) if ref[:, 0].mean() > 0 else float("nan")
            out[name] = res
        return out
    R["O2"]["corpus_channel"] = {g: channel(df) for g, df in groups.items() if df.height}

    # O2c conversational channel (context act -> response act)
    allper = per.filter(pl.col("speaker_kind") == "agent")
    conv_groups = {"leader": lead, "K_same": ksame, "V_same": vsame, "CTRL": ctrl,
                   "kimi_period": allper.filter(pl.col("group") == "kimi"),
                   "village_period": allper.filter(pl.col("group") == "village")}
    R["O2"]["conversation"] = {}
    for g, df in conv_groups.items():
        d = df.filter(pl.col("prev_act").is_not_null())
        if d.height < 3:
            continue
        x, y = d["prev_act"].to_list(), d["primary"].to_list()
        R["O2"]["conversation"][g] = {
            "fine": L.sample_channel_test(x, y, n_null=2000, seed=RNG_SEED),
            "coarse": L.sample_channel_test([L.COARSE[a] for a in x], [L.COARSE[a] for a in y], n_null=2000,
                                            seed=RNG_SEED)}
    # corpus's own policy: last snippet line -> target
    last = [s.strip().split("\n")[-1] for s in C["chat_snippet"].to_list()]
    xs = [L.plan_acts(s)["primary"] for s in last]
    R["O2"]["conversation"]["corpus"] = {
        "fine": L.sample_channel_test(xs, cprim, n_null=2000, seed=RNG_SEED),
        "coarse": L.sample_channel_test([L.COARSE[a] for a in xs], [L.COARSE[a] for a in cprim], n_null=2000,
                                        seed=RNG_SEED)}

    # ------------------------------------------------------------------ O3 embedding level
    zbarC, zbarK = zC.mean(0), Z[[zpos[(m, "field")] for m in kfield["message_id"].to_list()]].mean(0)
    def dstat(df, sset="period"):
        Zg = Z[[zpos[(m, sset)] for m in df["message_id"].to_list()]]
        return L.cos_rows(Zg, zbarC) - L.cos_rows(Zg, zbarK), L.cos_rows(Zg, zbarC), L.cos_rows(Zg, zbarK)
    D = {g: dstat(df) for g, df in groups.items() if df.height}
    dO = L.cos_rows(zO, zbarC) - L.cos_rows(zO, zbarK)
    R["O3"] = {"d": {g: _boot_ci(v[0]) for g, v in D.items()} | {"offline": _boot_ci(dO)},
               "cos_C": {g: _boot_ci(v[1]) for g, v in D.items()},
               "cos_K": {g: _boot_ci(v[2]) for g, v in D.items()},
               "cos_C_K_centroids": L.cos(zbarC, zbarK)}
    R["O3"]["tests"] = {f"d:leader>{o}": L.perm_mean_diff(D["leader"][0], D[o][0], seed=RNG_SEED)
                        for o in ("CTRL", "K_same", "V_same") if o in D}
    # O3c context similarity
    def ctxsim(df):
        ix = [zpos[(m, "period")] for m in df["message_id"].to_list()]
        a, b = Z[ix], Zc[ix]
        ok = ~np.isnan(b).any(1)
        return np.array([L.cos(u, v) for u, v in zip(a[ok], b[ok])])
    CS = {g: ctxsim(df) for g, df in groups.items() if df.height}
    R["O3"]["ctx_sim"] = {g: _boot_ci(v) for g, v in CS.items()}
    R["O3"]["tests"]["ctx:leader>CTRL"] = L.perm_mean_diff(CS["leader"], CS["CTRL"], seed=RNG_SEED)

    # O3b field level (day field removed) + invariance check of the Kimi field
    R["O3"]["field"] = _field_level(M, Z, zpos, zC, lead, cfg)

    # lexical context copy (rival R2): per message, bigram copy from the previous others' messages, token-matched
    ntoks_c = sum(len(L.tokens(s)) for s in c_txt)
    perall = per.sort("t")
    ptxt = [T.get(m) or "" for m in perall["message_id"].to_list()]
    pid = perall["message_id"].to_list()
    pagent = perall["agent"].to_list()
    pkind = perall["speaker_kind"].to_list()
    pos = {m: i for i, m in enumerate(pid)}

    def ctx_copy(df):
        out = []
        for m, a in zip(df["message_id"].to_list(), df["agent"].to_list()):
            i = pos[m]
            ref, nt, j = set(), 0, i - 1
            while j >= 0 and nt < ntoks_c:
                if not (pkind[j] == "agent" and pagent[j] == a):
                    tok = L.tokens(ptxt[j])
                    ref |= L.ngram_set(tok, 2)
                    nt += len(tok)
                j -= 1
            out.append(L.copy_fraction(T.get(m) or "", ref, 2) if nt >= 0.5 * ntoks_c else np.nan)
        return np.array(out)
    CC = {g: ctx_copy(df) for g, df in groups.items() if df.height}
    R["R2"] = {"ctx_c2": {g: _boot_ci(v) for g, v in CC.items()},
               "ctx_c2_minus_corpus_c2": {g: _boot_ci(CC[g] - LX[g]["c2"]) for g in CC},
               "test_ctx_c2:leader>CTRL": L.perm_mean_diff(CC["leader"], CC["CTRL"], seed=RNG_SEED)}

    # features table (no text)
    feats = []
    for g, df in groups.items():
        if g == "CTRL":
            continue
        for i, m in enumerate(df["message_id"].to_list()):
            feats.append({"message_id": m, "group": g, "agent": df["agent"][i], "t": df["t"][i],
                          "primary": df["primary"][i], "prev_act": df["prev_act"][i],
                          **{k: float(LX[g][k][i]) for k in ("c1", "c2", "c3", "r_corpus", "r_base")},
                          "ntok": int(LX[g]["ntok"][i]), "d": float(D[g][0][i]) if g in D else None,
                          "ctx_sim": None, "ctx_c2": float(CC[g][i]) if g in CC else None})
    pl.DataFrame(feats, infer_schema_length=None).write_parquet(pdir / "features.parquet", compression="zstd")
    (pdir / "results.json").write_text(json.dumps(R, indent=1, default=_np))
    return R


def _marker_class(w):
    """Coarse class of a marker n-gram for reporting (no text in committed files)."""
    toks = [w] if isinstance(w, str) else list(w)
    if any(t == "<agent>" for t in toks):
        return "agent-address"
    if any(t in ("@", "—", "–", "**", "!", "?", ":") for t in toks):
        return "punctuation/markup"
    if any(t in ("<num>", "<uri>", "<url>", "<hash>", "<email>", "<emoji>") for t in toks):
        return "masked token"
    if all(t in L.STOP for t in toks):
        return "function words"
    return "content words"


def _deltas(M, Z, zpos):
    """Day-field residuals: z minus the mean of other agents' vectors on the same PT day (within this table)."""
    rows = M.filter(pl.col("set").is_in(["period", "field", "background"]) & (pl.col("speaker_kind") == "agent"))
    rows = rows.unique("message_id", keep="first")
    ix = np.array([zpos[(m, s)] for m, s in zip(rows["message_id"].to_list(), rows["set"].to_list())])
    Zr = Z[ix]
    day, ag = rows["pt_date"].to_list(), rows["agent"].to_list()
    sums: dict = {}
    for i, (d, a) in enumerate(zip(day, ag)):
        s = sums.setdefault(d, {}).setdefault(a, [np.zeros(Z.shape[1]), 0])
        s[0] += Zr[i]
        s[1] += 1
    out = {}
    for i, (m, d, a) in enumerate(zip(rows["message_id"].to_list(), day, ag)):
        tot = sum(v[0] for k, v in sums[d].items() if k != a)
        n = sum(v[1] for k, v in sums[d].items() if k != a)
        if n:
            out[m] = Zr[i] - tot / n
    return out, rows


def _field_level(M, Z, zpos, zC, lead, cfg):
    """Base (Kimi K2.6) and corpus fields are fixed, agent-level properties estimated once on the non-holdout G44
    table (exception (b)); the leader's field is estimated in the period being analyzed."""
    MG = pl.read_parquet(G44 / "messages.parquet")
    VG = np.load(G44 / "vectors.npz")
    zposG = {(m, s): i for i, (m, s) in enumerate(zip(VG["message_id"], VG["set"]))}
    ZG = VG["z"]
    dG, rowsG = _deltas(MG, ZG, zposG)
    ag, goal, mid = rowsG["agent"].to_list(), rowsG["goal_no"].to_list(), rowsG["message_id"].to_list()
    live_ids = set(MG.filter(pl.col("live") & (pl.col("group") == "leader"))["message_id"].to_list())
    kimi = [(m, g) for m, a, g in zip(mid, ag, goal) if a == L.KIMI and m in dG and m not in live_ids]
    A = [dG[m] for m, g in kimi if g in (38, 40, 42)]
    B = [dG[m] for m, g in kimi if g in (39, 41, 44)]
    hKA, hKB = np.mean(A, 0), np.mean(B, 0)
    cross = {}
    for a in set(ag):
        if a in (L.KIMI, 28, 30):
            continue
        Ag = [dG[m] for m, aa, g in zip(mid, ag, goal) if aa == a and g in (38, 40, 42) and m in dG]
        Bg = [dG[m] for m, aa, g in zip(mid, ag, goal) if aa == a and g in (39, 41, 44) and m in dG]
        if len(Ag) >= 10 and len(Bg) >= 10:
            cross[int(a)] = L.cos(hKA, np.mean(Bg, 0))
    same = L.cos(hKA, hKB)
    inv_pass = bool(cross) and same > max(cross.values())
    hK = np.mean([dG[m] for m, g in kimi], 0)
    ft = MG.filter((pl.col("set") == "period") & (pl.col("speaker_kind") == "agent")
                   & (pl.col("group") != "leader") & (pl.col("t") < L.LIVE_START))
    zft = ZG[[zposG[(m, "period")] for m in ft["message_id"].to_list()]].mean(0)
    hC = zC.mean(0) - zft
    dP, _ = _deltas(M, Z, zpos)
    hl = [dP[m] for m in lead["message_id"].to_list() if m in dP]
    out = {"kimi_split_half_cos": same, "cross_agent_cos": cross, "invariance_pass": inv_pass,
           "n_kimi_A": len(A), "n_kimi_B": len(B), "n_leader": len(hl)}
    if hl:
        hL = np.mean(hl, 0)
        rng = np.random.default_rng(RNG_SEED)
        bs = []
        for _ in range(2000):
            hb = np.mean([hl[i] for i in rng.integers(0, len(hl), len(hl))], 0)
            bs.append(L.cos(hb, hC) - L.cos(hb, hK))
        out.update({"cos_hL_hC": L.cos(hL, hC), "cos_hL_hK": L.cos(hL, hK), "cos_hC_hK": L.cos(hC, hK),
                    "diff": L.cos(hL, hC) - L.cos(hL, hK),
                    "diff_ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                    "p_diff_le_0": float(np.mean(np.array(bs) <= 0))})
    return out


def _np(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    raise TypeError(type(o))
