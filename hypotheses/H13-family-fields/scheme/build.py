"""H13 scheme: per goal-period unit content vectors, style features, marker counts and talk-spin pair-days.

For each unit (goal period, split at step changes; same units as H01) writes data/processed/H13-family-fields/G<NN>/:
  u<unit>_agent_day.parquet      agent, pt_date, lab, n (chat statements), room (modal chat room), purity, words, role,
                                 marker counts m_<k>, mean style features f_<k>
  u<unit>_agent_day_raw.npy      (rows of agent_day) x 32: mean of unit-normalized regime-whitened statement vectors
  u<unit>_agent_day_sty.npy      same after within-unit OLS residualization on 20 style features (renormalized)
  u<unit>_win30.parquet / _raw.npy   same (raw only) per agent x day x 30-min window
  u<unit>_talk_pairday.parquet   pt_date, i, j, c0, c0_sur (cross-day surrogate within the unit), act_i, act_j,
                                 room_i, room_j (agent-day modal chat rooms; -1 unknown)
No message text is written; only counts and vectors.

Usage: uv run python hypotheses/H13-family-fields/scheme/build.py [--units 35,36b,...]
The confirmatory script imports build_units(..., allow_holdout=True, out=<confirm dir>); exploration asserts no holdout.

Round 1b (improved data, 2026-10-04), the old path above stays the default:
  ... build.py --r1b [--model bge_small|gte_modernbert] [--dedupe none|copies|restatements] [--talk fixed|old]
writes data/processed/H13-family-fields/r1b/<model>_<dedupe>/ with the same files plus u<unit>_agent_day_styp.npy
(shared DQ5 style_resid_period vectors). Statement vectors come from the shared DQ5 statement-level files
(statements_white32_<model>.npy: regime-whitened, unit-normalized; for bge identical to the old own whitening),
talk spins from activity_bins_fixed (DQ8) unless --talk old, and dedupe drops statements flagged by DQ5's
statement_flags (copies = self_repeat_both, restatements = self_repeat in either model).
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import OUT as SH, REVISION, git_commit, holdout_mask, load_whitener, rows  # noqa: E402

DATA = ROOT / "data/processed/H13-family-fields"
ED = SH / "embeddings"
DIM = 32

# goal-period units (split at step changes inside the period; identical to H01's units)
UNITS = {
    "35": ("G35", 35, "II", "2026-03-16", "2026-03-20"),
    "36b": ("G36", 36, "III", "2026-03-24", "2026-03-27"),
    "37": ("G37", 37, "III", "2026-03-30", "2026-04-01"),
    "38a": ("G38", 38, "III", "2026-04-02", "2026-04-13"),
    "38b": ("G38", 38, "III", "2026-04-14", "2026-04-17"),
    "38c": ("G38", 38, "III", "2026-04-20", "2026-04-24"),
    "39": ("G39", 39, "III", "2026-04-27", "2026-05-01"),
    "40": ("G40", 40, "III", "2026-05-04", "2026-05-08"),
    "41": ("G41", 41, "III", "2026-05-11", "2026-05-15"),
    "42": ("G42", 42, "III", "2026-05-18", "2026-05-22"),
    "44": ("G44", 44, "III", "2026-05-26", "2026-05-29"),
    "51a": ("G51", 51, "III", "2026-07-06", "2026-07-08"),
    "51b": ("G51", 51, "III", "2026-07-09", "2026-08-04"),
    "51c": ("G51", 51, "III", "2026-08-05", "2026-08-24"),
    "51d": ("G51", 51, "III", "2026-08-25", "2026-09-02"),
    "51e": ("G51", 51, "III", "2026-09-03", "2026-09-04"),
}

# pre-registered marker list (card, Observables a5); regexes are case-insensitive, word-bounded
APOS = "['’]"
MARKERS = {
    "genuinely": r"\bgenuinely\b", "honestly": r"\bhonestly\b", "appreciate": r"\bappreciat\w*",
    "youre_right": rf"\byou{APOS}?re (?:absolutely )?right\b", "wonderful": r"\bwonderful\b", "beautiful": r"\bbeautiful\w*",
    "fascinating": r"\bfascinat\w*", "i_think": r"\bi think\b",
    "per": r"\bper\b", "eta": r"\beta\b", "ack": r"\back\b", "fyi": r"\bfyi\b", "noted": r"\bnoted\b",
    "confirmed": r"\bconfirmed\b", "verified": r"\bverified\b", "blocked": r"\bblocked\b", "next_step": r"\bnext steps?\b",
    "will_do": r"\bwill do\b", "on_it": r"\bon it\b", "standing_by": r"\bstanding by\b",
    "delve": r"\bdelv\w*", "crucial": r"\bcrucial\w*", "robust": r"\brobust\w*", "comprehensive": r"\bcomprehensive\w*",
    "seamless": r"\bseamless\w*", "leverage": r"\bleverag\w*", "indeed": r"\bindeed\b", "i_will": r"\bi will\b",
    "i_am": r"\bi am\b",
    "absolutely": r"\babsolutely\b", "perfect": r"\bperfect\w*", "excellent": r"\bexcellent\b", "great": r"\bgreat\b",
    "amazing": r"\bamazing\b", "awesome": r"\bawesome\b", "thanks": r"\bthanks?\b|\bthank you\b",
    "sorry": r"\bsorry\b|\bapologi\w*",
}

STYLE = ["log_chars", "lines", "bullet_share", "headers", "bold", "emoji", "excl", "ques", "urls", "backticks",
         "digit_share", "upper_share", "at", "emdash", "fps", "fpp", "sp", "colon", "word_len", "parens"]


def unit_days(u, allow_holdout=False):
    g, goal, reg, a, b = UNITS[u] if isinstance(u, str) else u
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no"])
    d = cal.filter((pl.col("pt_date") >= a) & (pl.col("pt_date") <= b) & (pl.col("goal_no") == goal))
    days = sorted(d["pt_date"].to_list())
    held = holdout_mask(days, [goal] * len(days))
    if not allow_holdout:
        assert not any(held), f"holdout day in exploratory unit {u}: {[x for x, h in zip(days, held) if h]}"
    return days


# ----------------------------------------------------------------------------- text features (numbers only)
def text_features(txt: pl.DataFrame) -> pl.DataFrame:
    t = pl.col("text").fill_null("")
    nch = t.str.len_chars().cast(pl.Float64)
    nl = (t.str.count_matches("\n") + 1).cast(pl.Float64)
    letters = t.str.count_matches(r"[A-Za-z]").cast(pl.Float64)
    words = t.str.count_matches(r"\b\w+\b").cast(pl.Float64)
    per100 = lambda e: e.cast(pl.Float64) * 100.0 / (nch + 1.0)
    perw = lambda e: e.cast(pl.Float64) / (words + 1.0)
    feats = [
        (nch + 1).log().alias("f_log_chars"),
        nl.log().alias("f_lines"),
        (t.str.count_matches(r"(?m)^\s*(?:[-*•]|\d+[.)])\s").cast(pl.Float64) / nl).alias("f_bullet_share"),
        t.str.count_matches(r"(?m)^\s*#{1,6}\s").cast(pl.Float64).alias("f_headers"),
        (t.str.count_matches(r"\*\*").cast(pl.Float64) / 2).alias("f_bold"),
        t.str.count_matches(r"[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]").cast(pl.Float64).alias("f_emoji"),
        per100(t.str.count_matches("!")).alias("f_excl"),
        per100(t.str.count_matches(r"\?")).alias("f_ques"),
        t.str.count_matches(r"https?://").cast(pl.Float64).alias("f_urls"),
        t.str.count_matches("`").cast(pl.Float64).alias("f_backticks"),
        (t.str.count_matches(r"\d").cast(pl.Float64) / (nch + 1)).alias("f_digit_share"),
        (t.str.count_matches(r"[A-Z]").cast(pl.Float64) / (letters + 1)).alias("f_upper_share"),
        t.str.count_matches("@").cast(pl.Float64).alias("f_at"),
        t.str.count_matches("—").cast(pl.Float64).alias("f_emdash"),
        perw(t.str.count_matches(r"(?i)\b(?:i|me|my|mine|myself)\b")).alias("f_fps"),
        perw(t.str.count_matches(r"(?i)\b(?:we|us|our|ours|ourselves)\b")).alias("f_fpp"),
        perw(t.str.count_matches(r"(?i)\b(?:you|your|yours|yourself)\b")).alias("f_sp"),
        per100(t.str.count_matches(":")).alias("f_colon"),
        (letters / (words + 1)).alias("f_word_len"),
        per100(t.str.count_matches(r"[()]")).alias("f_parens"),
        words.alias("words"),
    ]
    marks = [t.str.count_matches("(?i)" + p).cast(pl.Int32).alias("m_" + k) for k, p in MARKERS.items()]
    return txt.select("message_id", *feats, *marks)


def roles_for(days):
    """agent -> assigned role (agent_goals.short_name) valid on most of the unit's days (#51 era); else None."""
    ro = pl.read_parquet(SH / "roster.parquet", columns=["agent", "agent_id"])
    aid = dict(zip(ro["agent_id"].to_list(), ro["agent"].to_list()))
    cnt = {}
    for g in rows("agent_goals"):
        a = aid.get(g["agent_id"])
        if a is None:
            continue
        s = g["start_time"][:10]
        e = (g["end_time"] or "9999-12-31")[:10]
        for d in days:
            if s <= d < e or (s == e == d):
                cnt.setdefault(a, {}).setdefault(g["short_name"], 0)
                cnt[a][g["short_name"]] += 1
    return {a: max(v, key=v.get) for a, v in cnt.items()}


# ----------------------------------------------------------------------------- talk spins
def corr_cols(X, Y):
    X = X - X.mean(0); Y = Y - Y.mean(0)
    sx, sy = X.std(0), Y.std(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        C = (X.T @ Y) / len(X) / np.outer(sx, sy)
    C[~np.isfinite(C)] = np.nan
    return C


def talk_pairdays(days, agent_room, table="activity_bins"):
    ab = pl.read_parquet(SH / f"{table}.parquet", columns=["pt_date", "minute", "agent", "state"]) \
           .filter(pl.col("pt_date").is_in(days))
    agents = np.array(sorted(ab["agent"].unique().to_list()))
    N = len(agents)
    S, valid, act = {}, {}, {}
    for (d,), g in ab.group_by("pt_date", maintain_order=True):
        L = int(g["minute"].max()) + 1
        A = -np.ones((L, N), dtype=np.float64)
        present = np.zeros(N, bool)
        ai = np.searchsorted(agents, g["agent"].to_numpy())
        present[np.unique(ai)] = True
        A[g["minute"].to_numpy(), ai] = np.where(g["state"].to_numpy() == 4, 1.0, -1.0)
        flips = (A[1:] != A[:-1]).sum(0)
        S[d], valid[d], act[d] = A, present & (flips >= 4), (A.mean(0) + 1) / 2
    out = []
    pi, pj = np.triu_indices(N, 1)
    for d in days:
        if d not in S:
            continue
        sel = valid[d][pi] & valid[d][pj]
        a, b = pi[sel], pj[sel]
        C0 = corr_cols(S[d], S[d])
        sur = []
        for e in days:
            if e == d or e not in S:
                continue
            L = min(len(S[d]), len(S[e]))
            B = corr_cols(S[d][:L], S[e][:L])          # B[i, j] = corr(i on day d, j on day e)
            B1 = np.where(valid[d][:, None] & valid[e][None, :], B, np.nan)
            B2 = np.where(valid[e][:, None] & valid[d][None, :], B.T, np.nan)
            with np.errstate(invalid="ignore"):
                sur.append(np.nanmean(np.stack([B1[a, b], B2[a, b]]), 0))
        c_sur = np.nanmean(np.array(sur), 0) if sur else np.full(len(a), np.nan)
        rr = lambda k: np.array([agent_room.get((int(agents[x]), d), -1) for x in k], dtype=np.int16)
        out.append(pl.DataFrame({"pt_date": [d] * len(a), "i": agents[a].astype(np.int8), "j": agents[b].astype(np.int8),
                                 "c0": C0[a, b].astype(np.float32), "c0_sur": c_sur.astype(np.float32),
                                 "act_i": act[d][a].astype(np.float32), "act_j": act[d][b].astype(np.float32),
                                 "room_i": rr(a), "room_j": rr(b)}))
    return pl.concat(out) if out else None


# ----------------------------------------------------------------------------- main build
def build_units(units: dict, out: Path, allow_holdout=False, tag="explore", model=None, dedupe="none",
                talk_table="activity_bins"):
    """model=None: the round-1 path (own whitening of chat_bge_small). model in {bge_small, gte_modernbert}: round 1b,
    shared DQ5 statement-level white32 vectors, plus the shared style_resid_period vectors (u*_agent_day_styp.npy)."""
    t0 = time.time()
    out.mkdir(parents=True, exist_ok=True)
    roster = pl.read_parquet(SH / "roster.parquet", columns=["agent", "lab", "name"])
    st = pl.read_parquet(ED / "statements.parquet").with_row_index("srow").filter(pl.col("kind") == "chat")
    if dedupe != "none":
        fl = pl.read_parquet(SH / "statement_flags.parquet", columns=["srow", "self_repeat", "self_repeat_both"])
        col = {"copies": "self_repeat_both", "restatements": "self_repeat"}[dedupe]
        drop = fl.filter(pl.col(col))["srow"]
        n0 = st.height
        st = st.filter(~pl.col("srow").is_in(drop))
        print(f"[{tag}] dedupe={dedupe}: dropped {n0 - st.height} of {n0} chat statements", flush=True)
    if model is not None:
        sys.path.insert(0, str(ROOT / "infra/shared"))
        from embed_models import MODELS  # noqa: E402
        sfx = MODELS[model]["suffix"]
        W32 = np.load(ED / f"statements_white32_{sfx}.npy", mmap_mode="r")
        WSP = np.load(ED / f"statements_style_resid_period32_{sfx}.npy", mmap_mode="r")
    cidx = pl.read_parquet(ED / "chat_index.parquet").with_row_index("src_row")
    Ec = np.load(ED / "chat_bge_small.npy", mmap_mode="r")
    meta = {}
    whit = {}
    for u, spec in units.items():
        gdir, goal, reg, a, b = spec
        days = unit_days(spec, allow_holdout=allow_holdout)
        s = st.filter(pl.col("pt_date").is_in(days)).join(cidx, on="src_row", how="left").sort("t")
        if s.height == 0:
            continue
        txt = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).join(
            s.select("message_id"), on="message_id", how="semi")
        feats = text_features(txt)
        del txt
        s = s.join(feats, on="message_id", how="left")
        if model is None:
            if reg not in whit:
                whit[reg] = load_whitener(reg, DIM)
            Z = whit[reg](np.asarray(Ec[s["src_row"].to_numpy()], dtype=np.float32))
            U = Z / np.linalg.norm(Z, axis=1, keepdims=True)
        else:
            U = np.asarray(W32[s["srow"].to_numpy()], dtype=np.float32)
            U = U / np.linalg.norm(U, axis=1, keepdims=True)
            Usp = np.asarray(WSP[s["srow"].to_numpy()], dtype=np.float32)
            Usp = Usp / np.where(np.linalg.norm(Usp, axis=1, keepdims=True) > 0, np.linalg.norm(Usp, axis=1, keepdims=True), 1)
        # within-unit style residualization (OLS on standardized style features, all agents' statements)
        F = s.select([f"f_{k}" for k in STYLE]).to_numpy().astype(np.float64)
        F = np.nan_to_num(F)
        F = (F - F.mean(0)) / np.where(F.std(0) > 0, F.std(0), 1)
        X = np.column_stack([np.ones(len(F)), F])
        B, *_ = np.linalg.lstsq(X, U.astype(np.float64), rcond=None)
        R = U - (X @ B)
        r2_style = float(1 - (R ** 2).sum() / ((U - U.mean(0)) ** 2).sum())
        Us = R / np.linalg.norm(R, axis=1, keepdims=True)
        roles = roles_for(days) if goal >= 51 else {}
        s = s.with_columns(pl.Series("row", np.arange(s.height)))
        gd = out / gdir
        gd.mkdir(parents=True, exist_ok=True)
        # agent-day
        ad = (s.group_by("agent", "pt_date", maintain_order=True)
              .agg(pl.col("row"), pl.len().alias("n"), pl.col("words").sum(),
                   pl.col("room").mode().first().alias("room"),
                   ((pl.col("room") == pl.col("room").mode().first()).mean()).alias("purity"),
                   *[pl.col("m_" + k).sum() for k in MARKERS], *[pl.col(f"f_{k}").mean() for k in STYLE])
              .sort("agent", "pt_date").join(roster.select("agent", "lab"), on="agent", how="left")
              .with_columns(pl.col("agent").replace_strict(roles, default=None, return_dtype=pl.String).alias("role")))
        Vr = np.stack([U[r].mean(0) for r in ad["row"].to_list()]).astype(np.float32)
        Vs = np.stack([Us[r].mean(0) for r in ad["row"].to_list()]).astype(np.float32)
        ad.drop("row").write_parquet(gd / f"u{u}_agent_day.parquet", compression="zstd")
        np.save(gd / f"u{u}_agent_day_raw.npy", Vr)
        np.save(gd / f"u{u}_agent_day_sty.npy", Vs)
        if model is not None:
            np.save(gd / f"u{u}_agent_day_styp.npy", np.stack([Usp[r].mean(0) for r in ad["row"].to_list()]).astype(np.float32))
        # agent x 30-min window
        w = (s.filter(pl.col("win30").is_not_null()).group_by("agent", "pt_date", "win30", maintain_order=True)
             .agg(pl.col("row"), pl.len().alias("n"), pl.col("room").mode().first().alias("room"))
             .sort("agent", "pt_date", "win30"))
        Vw = np.stack([U[r].mean(0) for r in w["row"].to_list()]).astype(np.float16)
        w.drop("row").write_parquet(gd / f"u{u}_win30.parquet", compression="zstd")
        np.save(gd / f"u{u}_win30_raw.npy", Vw)
        # talk spins
        agent_room = {(int(x), d): int(r) for x, d, r, p in ad.select("agent", "pt_date", "room", "purity").iter_rows()
                      if r is not None}
        tp = talk_pairdays(days, agent_room, talk_table)
        if tp is not None:
            tp.write_parquet(gd / f"u{u}_talk_pairday.parquet", compression="zstd")
        meta[u] = {"gdir": gdir, "goal_no": goal, "regime": reg, "days": days, "n_statements": int(s.height),
                   "n_agent_days": int(ad.height), "n_windows": int(w.height), "style_r2": r2_style,
                   "n_talk_pairdays": int(tp.height) if tp is not None else 0, "roles": {str(k): v for k, v in roles.items()}}
        print(f"[{tag}] unit {u}: {len(days)} days, {s.height} statements, {ad.height} agent-days, "
              f"style R2 {r2_style:.3f}, {time.time() - t0:.0f}s", flush=True)
    (out / "units.json").write_text(json.dumps(meta, indent=1))
    r1b = {"model": model, "dedupe": dedupe, "talk_table": talk_table} if model is not None else None
    prov = {"built_by": "hypotheses/H13-family-fields/scheme/build.py", "git_commit": git_commit(), "round_1b": r1b,
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/embeddings/statements", "shared/embeddings/chat_bge_small.npy",
                                   "shared/embeddings/whitening_<regime>.npz", "shared/chat_text (counts only)",
                                   "shared/activity_bins", "shared/roster", "shared/calendar", "raw/agent_goals"]}],
            "params": {"dim": DIM, "statements": "agent chat only", "style_features": STYLE, "markers": MARKERS,
                       "talk_spin": "activity_bins.state == 4, 1-min, >= 4 flips/day; cross-day surrogate within unit",
                       "units": {k: list(v) for k, v in units.items()}, "allow_holdout": allow_holdout},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1))
    return meta


def _arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


if __name__ == "__main__":
    sel = sys.argv[sys.argv.index("--units") + 1].split(",") if "--units" in sys.argv else list(UNITS)
    if "--r1b" in sys.argv:
        mdl, ded = _arg("--model", "bge_small"), _arg("--dedupe", "none")
        tt = "activity_bins_fixed" if _arg("--talk", "fixed") == "fixed" else "activity_bins"
        build_units({u: UNITS[u] for u in sel}, DATA / "r1b" / f"{mdl}_{ded}", tag=f"r1b {mdl} {ded}", model=mdl,
                    dedupe=ded, talk_table=tt)
    else:
        build_units({u: UNITS[u] for u in sel}, DATA)
