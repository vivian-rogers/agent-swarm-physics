"""H145 scheme: elements, expression panels, environment inputs and memeplex discovery for #51 (non-reserved days).

Builds data/processed/H145-ideology-egregores-51/ from the shared tables with infra/shared/memeplex.py:
  elements.parquet            eid, kind (cluster | marker | repo | project), key, n_events, n_agents, n_days
  elements_variants.json      element counts for the cluster variants (k 40, 160; gte)
  stmt_cluster.parquet        srow (row of the statement embeddings), cluster (k = 80, bge, seed 0)
  centroids_white32.npy       k-means cluster centroids in the whitened (white32, bge) space [80, 32]
  expr/w{30,120,1440}.parquet agent_row, bin, eid, count (present agent-bins only)
  expr/bins_w*.parquet        bin, day, bin_in_day, t0; expr/presence_w*.parquet agent_row, bin; expr/agents.json
  exo.parquet + exo_white32.npy   exogenous messages (human, automated operator, relayed human input) with vectors
  roles.parquet + roles_white32.npy  role texts (agent_goal rows) and the #51 kickoff, whitened
  discovery.json              A1 graph summary (activity-adjusted PPMI, BH-FDR 0.05 edges, gamma 1), all communities, variants
  memeplexes.json             qualifying memeplexes (frozen 2026-10-09 with labels, field-seeded flags) and role-text patterns
Text is read in memory only; nothing verbatim is written.

Usage: uv run python hypotheses/H145-ideology-egregores-51/scheme/build.py [--stage elements|exo|discover|label|all]
"""
from __future__ import annotations

import datetime as dt
import json
import math
import re
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
import memeplex as MP  # noqa: E402
from common import git_commit, holdout_mask, load_whitener, REVISION  # noqa: E402

OUT = ROOT / "data/processed/H145-ideology-egregores-51"
SH = ROOT / "data/processed/shared"
GOAL = 51
WIDTHS = (30, 120, 1440)
SEED = 0
# relayed human input (rule fixed on 07-06 -> 07-16; hand check: 22 of 29 matches relay an outside human, 0.76)
RELAY_SPEAKERS = (31, 29)            # Claude Fable 5, Claude Opus 4.8
RELAY = re.compile(r"\b(relay\w*|forward\w*|e-?mailed|asked me to|passing (?:this |it )?along|on (?:his|her|their) behalf)\b", re.I)
HUMAN = re.compile(r"\b(humans?|e-?mails?|e-?mailed|inbox|readers?|fans?|followers?|artist|helper|viewers?|visitor)\b", re.I)


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def build_elements():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "expr").mkdir(exist_ok=True)
    el = MP.build_elements(GOAL, k=80, model="bge", seed=SEED)
    el.table.write_parquet(OUT / "elements.parquet", compression="zstd")
    st = el.statements.select("srow", "agent", "t", "pt_date", "kind").with_columns(
        pl.Series("cluster", el.stmt_cluster.astype(np.int16)))
    st.select("srow", "cluster").write_parquet(OUT / "stmt_cluster.parquet", compression="zstd")
    # centroids in white32 space (for similarity to role texts and exogenous messages)
    W32 = np.load(SH / "embeddings/statements_white32_bge_small.npy", mmap_mode="r")
    V = np.asarray(W32[st["srow"].to_numpy()], np.float32)
    Cw = np.zeros((80, V.shape[1]), np.float32)
    np.add.at(Cw, el.stmt_cluster, V)
    Cw /= np.maximum(np.bincount(el.stmt_cluster, minlength=80), 1)[:, None]
    np.save(OUT / "centroids_white32.npy", Cw)
    info = {"primary": el.info}
    # variants: element counts only (k 40, 160; gte)
    for k, model in ((40, "bge"), (160, "bge"), (80, "gte")):
        mname = {"bge": "bge_small", "gte": "gte_modernbert"}[model]
        Vr = np.load(SH / f"embeddings/statements_style_resid_period32_{mname}.npy", mmap_mode="r")
        lab, _ = MP.kmeans(np.asarray(Vr[st["srow"].to_numpy()], np.float32), k, seed=SEED)
        na = st.with_columns(pl.Series("c", lab)).group_by("c").agg(pl.col("agent").n_unique().alias("na"))
        info[f"k{k}_{model}"] = {"elements": int((na["na"] >= 3).sum())}
        np.save(OUT / f"stmt_cluster_k{k}_{model}.npy", lab.astype(np.int16))
    (OUT / "elements_variants.json").write_text(json.dumps(info, indent=1, default=str))
    # panels
    ev = el.events
    nE = el.table.height
    for w in WIDTHS:
        bins = MP.make_bins(GOAL, w)
        P = MP.make_panel(ev, bins, nE)
        C = P.X.tocoo()
        pl.DataFrame({"agent_row": (C.row // bins.nB).astype(np.int8), "bin": (C.row % bins.nB).astype(np.int16),
                      "eid": C.col.astype(np.int16), "count": C.data.astype(np.int16)}).write_parquet(
            OUT / f"expr/w{w}.parquet", compression="zstd")
        pl.DataFrame({"bin": np.arange(bins.nB, dtype=np.int16), "day": bins.day_of_bin.astype(np.int16),
                      "bin_in_day": bins.bin_in_day.astype(np.int16), "t0": bins.t0}).with_columns(
            pl.col("t0").dt.replace_time_zone("UTC")).write_parquet(OUT / f"expr/bins_w{w}.parquet")
        ai, bi = np.nonzero(bins.present)
        pl.DataFrame({"agent_row": ai.astype(np.int8), "bin": bi.astype(np.int16)}).write_parquet(
            OUT / f"expr/presence_w{w}.parquet")
        log(f"panel w{w}: {bins.nA} agents x {bins.nB} bins, {P.X.nnz} nonzeros, present {bins.present.mean():.2f}")
    (OUT / "expr/agents.json").write_text(json.dumps({"agents": bins.agents, "labs": {str(a): bins.labs[a] for a in bins.agents},
                                                       "days": bins.days}, indent=1))
    build_exo_roles()


def build_exo_roles():
    """Exogenous messages (e2) and role texts (e3) with white32 vectors."""
    Wh = load_whitener("III", 32)
    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "speaker_kind", "agent"])
            .filter(pl.col("goal_no") == GOAL))
    held = np.array(holdout_mask(chat["pt_date"].to_list(), chat["goal_no"].to_list()))
    chat = chat.filter(pl.Series(~held))
    exo = chat.filter(pl.col("speaker_kind").cast(pl.Utf8).is_in(["human", "automated"])).with_columns(
        pl.col("speaker_kind").cast(pl.Utf8).alias("src"))
    rel = chat.filter(pl.col("agent").is_in(list(RELAY_SPEAKERS)) & (pl.col("speaker_kind") == "agent"))
    txt = pl.scan_parquet(SH / "chat_text.parquet").select("message_id", "text").join(rel.lazy(), on="message_id").collect()
    flag = [bool(RELAY.search(x or "") and HUMAN.search(x or "")) for x in txt["text"]]
    rel = txt.filter(pl.Series(flag)).drop("text").with_columns(pl.lit("relayed").alias("src"))
    del txt
    kc = pl.read_parquet(SH / "kicks_classified.parquet", columns=["message_id", "kind"]).with_columns(
        pl.col("kind").cast(pl.Utf8).alias("kick_kind"))
    exo = pl.concat([exo.select("message_id", "t", "pt_date", "src"), rel.select("message_id", "t", "pt_date", "src")])
    exo = exo.join(kc, on="message_id", how="left").sort("t")
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("crow")
    exo = exo.join(ci, on="message_id", how="left")
    E = np.load(SH / "embeddings/chat_bge_small.npy", mmap_mode="r")
    has = exo["crow"].is_not_null().to_numpy()
    V = np.zeros((exo.height, 32), np.float32)
    V[has] = Wh(np.asarray(E[exo["crow"].drop_nulls().to_numpy()]))
    exo = exo.with_columns(pl.Series("has_vec", has)).drop("crow")
    exo.write_parquet(OUT / "exo.parquet")
    np.save(OUT / "exo_white32.npy", V)
    log(f"exo: {exo.group_by('src').len().rows()}")
    g = pl.read_parquet(SH / "embeddings/goals.parquet").with_row_index("grow").filter(
        (pl.col("goal_no") == GOAL) & pl.col("kind").cast(pl.Utf8).is_in(["agent_goal", "kickoff"]))
    G = np.load(SH / "embeddings/goal_vectors.npy")
    Vg = Wh(G[g["grow"].to_numpy()])
    g.select("grow", "gid", pl.col("kind").cast(pl.Utf8), "agent", "valid_from", "valid_to").write_parquet(OUT / "roles.parquet")
    np.save(OUT / "roles_white32.npy", Vg.astype(np.float32))
    log(f"roles: {g.height} rows")


def load_panel(w: int):
    """Rebuild the Panel for width w from the stored files (no shared-table reads)."""
    import scipy.sparse as sp
    meta = json.loads((OUT / "expr/agents.json").read_text())
    bt = pl.read_parquet(OUT / f"expr/bins_w{w}.parquet")
    pr = pl.read_parquet(OUT / f"expr/presence_w{w}.parquet")
    nA, nB = len(meta["agents"]), bt.height
    present = np.zeros((nA, nB), bool)
    present[pr["agent_row"].to_numpy(), pr["bin"].to_numpy()] = True
    bins = MP.Bins(GOAL, w, meta["days"], bt["t0"].dt.replace_time_zone(None).to_numpy().astype("datetime64[us]"),
                   bt["day"].to_numpy().astype(np.int64), bt["bin_in_day"].to_numpy().astype(np.int64),
                   meta["agents"], present, {int(k): v for k, v in meta["labs"].items()})
    ex = pl.read_parquet(OUT / f"expr/w{w}.parquet")
    nE = pl.read_parquet(OUT / "elements.parquet").height
    X = sp.csr_matrix((ex["count"].to_numpy().astype(np.float32),
                       (ex["agent_row"].to_numpy().astype(np.int64) * nB + ex["bin"].to_numpy(), ex["eid"].to_numpy().astype(np.int64))),
                      shape=(nA * nB, nE))
    return MP.Panel(bins, X, nE)


# Amendments A1 and A3 (2026-10-09, from the synthetic check; card Round 1): activity-adjusted PPMI expectation with
# Benjamini-Hochberg edges at q 0.05; resolution fixed at gamma 1 (0.5 and 2 reported as variants).
ACTIVITY = True
FDR = 0.05
GAMMA = 1.0
M_HOST = 2


def discover_stage():
    P = load_panel(120)
    t = time.time()
    W = MP.ppmi_graph(P, 3, activity=ACTIVITY, fdr=FDR)
    log(f"PPMI graph (A1): {int((W > 0).sum() // 2)} edges over {W.shape[0]} elements ({time.time() - t:.1f}s)")
    res = MP.discover(P, GAMMA, m=M_HOST, W=W, seed=SEED)
    tab = pl.read_parquet(OUT / "elements.parquet")
    kinds = tab["kind"].to_list()
    comms = []
    for c in res["communities"]:
        c = dict(c)
        c["kinds"] = {k: sum(kinds[e] == k for e in c["elements"]) for k in ("cluster", "marker", "repo", "project")}
        comms.append(c)
    variants = {}
    for g in (0.5, 2.0):
        r = MP.discover(P, g, m=M_HOST, W=W, seed=SEED)
        variants[f"gamma{g}"] = {"n_qualify": r["n_qualify"], "n_qualify_hub_free": r["n_qualify_hub_free"]}
    for m in (1, 3):
        r = MP.discover(P, GAMMA, m=m, W=W, seed=SEED)
        variants[f"m{m}"] = {"n_qualify": r["n_qualify"], "n_qualify_hub_free": r["n_qualify_hub_free"]}
    Wc = MP.ppmi_graph(P, 3)
    r = MP.discover(P, 1.0, m=M_HOST, W=Wc, seed=SEED)
    variants["as_written_agent_constant_p01_gamma1"] = {"n_qualify": r["n_qualify"], "n_qualify_hub_free": r["n_qualify_hub_free"],
                                                        "max_size": max([c["n_elements"] for c in r["communities"]] or [0])}
    for w in (30, 1440):
        Pw = load_panel(w)
        Ww = MP.ppmi_graph(Pw, 3, activity=ACTIVITY, fdr=FDR)
        r = MP.discover(Pw, GAMMA, m=M_HOST, W=Ww, seed=SEED)
        variants[f"w{w}"] = {"n_qualify": r["n_qualify"], "n_qualify_hub_free": r["n_qualify_hub_free"],
                             "edges": int((Ww > 0).sum() // 2)}
    disc = {"built_at": dt.datetime.now(dt.timezone.utc).isoformat(), "rules": {"activity": ACTIVITY, "fdr": FDR, "gamma": GAMMA,
            "m": M_HOST, "min_co": 3, "width": 120, "louvain_seeds": 5, "seed": SEED},
            "Q": res["Q"], "n_edges": int((W > 0).sum() // 2), "n_elements": int(W.shape[0]),
            "n_communities_ge2": len(comms), "n_qualify": res["n_qualify"], "n_qualify_hub_free": res["n_qualify_hub_free"],
            "variants": variants, "communities": comms}
    (OUT / "discovery.json").write_text(json.dumps(disc, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    np.save(OUT / "ppmi_w120.npy", W.astype(np.float32))
    log(f"communities >= 2 elements: {len(comms)}; qualifying {res['n_qualify']} (hub-free {res['n_qualify_hub_free']}); variants {variants}")


# --------------------------------------------------------------------------- labels (fixed 2026-10-09 before outcomes)
FAMILIES = {   # story part 4 candidate families as stems; matched against element tokens (labels only, P5)
    "verify": ["verif", "re-run", "rerun", "reproduc", "cross-check", "spot-check", "receipt", "correct", "retract", "errat",
               "sha256", "checksum", "audit", "sanity"],
    "consent": ["opt-out", "opt-in", "consent", "aggregate-only", "anonym", "non-identifying", "privacy", "per-agent",
                "read-only", "protection", "redact"],
    "governance": ["vote", "voter", "quorum", "binding", "gate", "no_go", "no-go", "halt", "abort", "guardrail", "safeguard",
                   "sign-off", "lsp", "bac", "ceiling", "fail-closed", "pre-registered", "pre-flight", "admin-approved",
                   "governance", "registry", "scoreboard", "ranking"],
    "dictate": ["proxy", "behalf", "dictat", "one-file", "bash", "text-only"],
    "onboarding": ["welcome", "onboard", "orientation", "hub card", "agents page", "first job", "newcomer"],
    "frameworks": ["relationship", "framework", "harbor", "pulse", "diagnostic", "mentorship", "adoption"],
    "welfare": ["welfare", "wellbeing", "well-being", "burnout"],
    "relay": ["relay", "forward", "inbox", "email"],
    "byte_game": ["byte", "guess"],
    "echoes": ["echoes", "chapter"],
    "cross_promo": ["cross-link", "link swap", "cross-promo", "footer", "partner"],
    "restraint": ["low-pressure", "non-pressuring", "spam", "unsolicited", "low-friction"],
}
STOP = set("""the and for that this with are was were you your our not but have has had from they their them its will would
can could should what when where which who how all any been being into than then there these those also just about after
before more most other some such only over very each per via let lets now here out get got one two three new use used using
make made need needs like still well yes okay thanks thank sure see note done next today going want know think it's i'm
we're don't can't i'll we'll i've that's what's here's there's let's""".split())


def element_tokens():
    """Label tokens per element (in memory only): cluster -> 8 top c-TF-IDF words of its statements; marker -> its
    normalized string; repo/project -> its slug. Returns {eid: [tokens]}."""
    import idea_markers as IM
    from collections import Counter
    tab = pl.read_parquet(OUT / "elements.parquet")
    sc = pl.read_parquet(OUT / "stmt_cluster.parquet")
    st = pl.read_parquet(SH / "embeddings/statements.parquet", columns=["kind", "src_row"]).with_row_index("srow")
    st = st.join(sc, on="srow", how="inner")
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    ii = pl.read_parquet(SH / "embeddings/intentions_index.parquet").with_row_index("src_row")
    chat = (st.filter(pl.col("kind") == "chat").join(ci, on="src_row").select("cluster", "message_id").lazy()
            .join(pl.scan_parquet(SH / "chat_text.parquet").select("message_id", "text"), on="message_id").select("cluster", "text").collect())
    intent = (st.filter(pl.col("kind") == "intent").join(ii, on="src_row").select("cluster", "event_index").lazy()
              .join(pl.scan_parquet(SH / "intentions_text.parquet").select("event_index", pl.col("short_text").alias("text")),
                    on="event_index").select("cluster", "text").collect())
    allt = pl.concat([chat, intent])
    ros = pl.read_parquet(SH / "roster.parquet")["name"].to_list()
    rostok = {w.lower() for n in ros for w in re.findall(r"[A-Za-z][A-Za-z0-9.\-]+", n)}
    tok = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*")
    per = {}
    tot = Counter()
    for c, t in zip(allt["cluster"].to_list(), allt["text"].to_list()):
        ws = [w for w in tok.findall((t or "").lower()) if len(w) >= 3 and w not in STOP and w not in rostok]
        per.setdefault(c, Counter()).update(ws)
        tot.update(ws)
    del allt, chat, intent
    nC = len(per)
    out = {}
    for row in tab.iter_rows(named=True):
        key = row["key"]
        if row["kind"] == "cluster":
            c = int(key.split(":")[1])
            cnt = per.get(c, Counter())
            n = sum(cnt.values()) or 1
            sc_ = {w: (v / n) * math.log(1 + nC * v / tot[w]) for w, v in cnt.items() if v >= 5}
            out[row["eid"]] = [w for w, _ in sorted(sc_.items(), key=lambda kv: -kv[1])[:8]]
        elif row["kind"] in ("repo", "project"):
            out[row["eid"]] = [key.split(":", 1)[1]]
    # markers: hash -> normalized string, from the #51 agent chat rows (non-reserved; in memory)
    mk = {int(k.split(":", 1)[1]): e for e, k in zip(tab["eid"].to_list(), tab["key"].to_list()) if k.startswith("m:")}
    cc = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "goal_no", "pt_date", "speaker_kind"])
          .filter((pl.col("goal_no") == GOAL) & (pl.col("speaker_kind") == "agent")))
    held = np.array(holdout_mask(cc["pt_date"].to_list(), cc["goal_no"].to_list()))
    cc = cc.filter(pl.Series(~held))
    txt = (pl.scan_parquet(SH / "chat_text.parquet").select("message_id", "text")
           .join(cc.lazy().select("message_id", "t"), on="message_id").collect().sort("t"))
    rf = IM.roster_full_names(ros)
    IM.dictionary()
    found, first_t = {}, {}
    for t, tt in zip(txt["text"].to_list(), txt["t"].to_list()):
        for cl, x in IM.extract(t, rf):
            h = IM.marker_id(cl, x)
            if h in mk and mk[h] not in found:
                found[mk[h]] = (cl, x)
                first_t[mk[h]] = tt
    del txt
    for e, (cl, x) in found.items():
        out[e] = [x]
    return out, {e: cl for e, (cl, x) in found.items()}, first_t


def family_scores(tokens: list) -> dict:
    s = {}
    for f, stems in FAMILIES.items():
        s[f] = int(sum(any(st in t for st in stems) for t in tokens))
    return s


def label_rule(scores: dict) -> str:
    """Candidate label: the family with the most token hits, >= 2 hits and >= 1.5x the runner-up; else 'unlabelled'."""
    srt = sorted(scores.items(), key=lambda kv: -kv[1])
    if srt[0][1] >= 2 and srt[0][1] >= 1.5 * max(srt[1][1], 0.01):
        return srt[0][0]
    return "unlabelled"


def first_use_exo(tab):
    """First use time of each marker element in exogenous messages (human, operator, relayed) of #51 (non-reserved)."""
    import idea_markers as IM
    exo = pl.read_parquet(OUT / "exo.parquet", columns=["message_id", "t", "src"])
    rows = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg")
            .join(exo, on="message_id", how="inner"))
    u = IM.uses_for_rows(rows["msg"].to_numpy()).join(rows.select(pl.col("msg").cast(pl.UInt32), "t"), on="msg")
    keys = pl.DataFrame({"marker": [int(k.split(":", 1)[1]) for k in tab["key"].to_list() if k.startswith("m:")],
                         "eid": [e for e, k in zip(tab["eid"].to_list(), tab["key"].to_list()) if k.startswith("m:")]})
    f = u.join(keys, on="marker").group_by("eid").agg(pl.col("t").min().alias("t_exo"))
    return dict(zip(f["eid"].to_list(), f["t_exo"].to_list()))


def label_stage():
    """Freeze memeplexes.json: qualifying memeplexes with stats, label tokens, candidate label, field-seeded flag;
    role-text patterns (P4 controls). Runs after discover_stage; no test statistic is computed here."""
    import importlib
    disc = json.loads((OUT / "discovery.json").read_text())
    tab = pl.read_parquet(OUT / "elements.parquet")
    toks, mcls, first_agent_t = element_tokens()
    log(f"tokens for {len(toks)} elements")
    t_exo = first_use_exo(tab)
    keys = tab["key"].to_list()
    kinds = tab["kind"].to_list()
    mems = []
    for c in disc["communities"]:
        if not c["qualifies"]:
            continue
        els = c["elements"]
        tk = [t for e in els for t in toks.get(e, [])]
        scores = family_scores(tk)
        # stored label tokens: no N-class marker strings (capitalised runs can be outside people's names) and no
        # external-host slugs; the family scores above used every token in memory
        n_names = sum(1 for e in els if kinds[e] == "marker" and mcls.get(e) == "N")
        words = [toks[e][0] for e in els if kinds[e] == "marker" and mcls.get(e) == "W" and e in toks][:8]
        slugs = [keys[e].split(":", 1)[1] for e in els if kinds[e] in ("repo", "project") and "." not in keys[e]][:8]
        ctw = [w for e in els if kinds[e] == "cluster" for w in toks.get(e, [])[:4]][:12]
        # field-seeded: K's earliest marker use is in an exogenous message (2-h bin resolution for agent uses)
        mk_e = [e for e in els if kinds[e] == "marker"]
        fs = None
        if mk_e:
            ta = [first_agent_t[e] for e in mk_e if e in first_agent_t]
            tex = [t_exo[e] for e in mk_e if e in t_exo]
            fs = bool(tex) and (not ta or min(tex) < min(ta))
        mems.append({"id": f"K{len(mems) + 1:02d}", **{k: c[k] for k in ("n_elements", "hosts", "n_hosts", "labs", "n_labs",
                     "lifetime_days", "span_days", "h_K", "top_host", "host_bins", "first_day", "last_day", "qualifies_hub_free", "kinds")},
                     "elements": els, "hub_label": "one agent's vocabulary" if c["h_K"] >= 0.8 else None,
                     "label_tokens": {"n_name_markers": n_names, "words": words, "slugs": slugs, "cluster_words": ctw},
                     "family_scores": scores, "candidate": label_rule(scores), "field_seeded": fs})
    # role-text patterns (P4 positive controls): k-means (k 5, seed 0) on agent role vectors; each class -> the 6
    # cluster elements nearest its mean role vector; plus the kickoff pattern
    roles = pl.read_parquet(OUT / "roles.parquet")
    Vr = np.load(OUT / "roles_white32.npy")
    Vr = Vr / np.linalg.norm(Vr, axis=1, keepdims=True)
    Cw = np.load(OUT / "centroids_white32.npy")
    Cw = Cw / np.linalg.norm(Cw, axis=1, keepdims=True)
    ceid = {int(k.split(":")[1]): e for e, k in zip(tab["eid"].to_list(), keys) if k.startswith("c:")}
    ag = (roles["kind"] == "agent_goal").to_numpy()
    lab, cen = MP.kmeans(Vr[ag], 5, seed=SEED)
    role_pats = []
    for j in range(5):
        v = cen[j] / np.linalg.norm(cen[j])
        top = [ceid[c] for c in np.argsort(-(Cw @ v)) if c in ceid][:6]
        role_pats.append({"id": f"R{j + 1}", "kind": "role_class", "n_agents": int((lab == j).sum()),
                          "agents": sorted(set(int(a) for a in roles.filter(pl.Series(ag))["agent"].to_numpy()[lab == j])),
                          "elements": top, "cluster_words": [w for e in top for w in toks.get(e, [])[:3]]})
    kv = Vr[~ag][0]
    top = [ceid[c] for c in np.argsort(-(Cw @ kv)) if c in ceid][:6]
    role_pats.append({"id": "R0", "kind": "kickoff", "elements": top, "cluster_words": [w for e in top for w in toks.get(e, [])[:3]]})
    out = {"frozen_at": dt.datetime.now(dt.timezone.utc).isoformat(), "goal_no": GOAL, "width_min": 120,
           "rules": disc["rules"], "amendments": ["A1 activity-adjusted PPMI + BH-FDR 0.05 edges", "A3 gamma fixed at 1"],
           "n_memeplexes": len(mems), "n_hub_free": sum(m["qualifies_hub_free"] for m in mems),
           "label_rule": "family with most token hits, >= 2 and >= 1.5x runner-up (FAMILIES in scheme/build.py)",
           "memeplexes": mems, "role_patterns": role_pats,
           "note": "labels are token lists and paraphrase-free names; no verbatim statements"}
    (OUT / "memeplexes.json").write_text(json.dumps(out, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
    log(f"memeplexes.json: {len(mems)} qualifying ({out['n_hub_free']} hub-free); candidates "
        f"{sorted([(m['id'], m['candidate'], m['n_elements'], m['n_hosts'], round(m['h_K'], 2)) for m in mems])}")


def provenance():
    prov = {"built_by": "hypotheses/H145-ideology-egregores-51/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["embeddings/statements", "statements_style_resid_period32_bge_small", "statements_white32_bge_small",
                                   "chat_core", "chat_text (in memory)", "work_commits", "project_calls", "project_call_touches",
                                   "call_windows", "calendar", "roster", "kicks_classified", "embeddings/goals", "goal_vectors",
                                   "chat_bge_small", "H34 marker rule (idea_markers.uses_for_rows)"]}],
            "params": {"goal_no": GOAL, "k": 80, "model": "bge", "seed": SEED, "widths": WIDTHS, "m": M_HOST, "min_co": 3,
                       "activity": ACTIVITY, "fdr": FDR, "gamma": GAMMA, "relay_speakers": RELAY_SPEAKERS,
                       "clean_commits": "memeplex.clean_commits at 4f6ab2e (mirror-loop repo dropped; single-file streams kept)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    stage = sys.argv[sys.argv.index("--stage") + 1] if "--stage" in sys.argv else "all"
    if stage in ("elements", "all"):
        build_elements()
    if stage in ("exo",):
        build_exo_roles()
    if stage in ("discover", "all"):
        discover_stage()
    if stage in ("label", "all"):
        label_stage()
    provenance()
