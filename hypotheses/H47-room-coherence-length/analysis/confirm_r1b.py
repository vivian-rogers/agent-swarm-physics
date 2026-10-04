"""H47 confirmatory script (LOCKED HOLDOUT), RE-FROZEN ON THE CORRECTED INPUTS (written 2026-10-04; NOT RUN).

Re-freeze of `confirm.py` (left byte-for-byte untouched; holdout.md ledger item 17). Written before any holdout data
was read. Details and reasons: `CONFIRM_R1B.md`.

What changed vs confirm.py
  * Village-off windows from the `outages_fixed` sidecar (`outages_fixed/{outages,stall_minutes}.parquet`), not the
    old `outages` / `stall_minutes` (built on the event-dropping activity_bins; joint silences 14.3% -> 5.3%).
  * Self-repeat dedupe from DQ5 `statement_flags` (chat rows): primary = restatements under either model
    (`self_repeat_bge | self_repeat_gte`); copies only (`self_repeat_both`) reported for C1. Round 1 used its own
    raw-bge cosine > 0.95 rule (= `self_repeat_bge`).
  * Both embedding models: bge-small (round-1 construction: raw bge, regime whitener, d = 32) and gte-modernbert (raw
    gte, `whitening_gte_modernbert_<regime>`, d = 32), each with its own goal / kickoff field directions
    (`goal_vectors[_gte_modernbert]`), its own raw vectors for the leadership projection (C4) and its own agent-day
    vectors for the detector (C5). Every criterion passes only if it passes under BOTH models (relabelled -r1b).
  * Not inputs: activity, visibility, work, failures, nudge targets. The room-relabel null permutes rooms within slots,
    so the scheduler cancels in C_B; no DQ8 trim is needed. Mention weights (`chat_mentions_clean`) feed only the
    descriptive tier ratio G.
  * Guards added: holdout-ledger gate (blocks a target with a same-family prior run in the same modality; none found).
  * Thresholds unchanged: the dry run below shows the corrected inputs do not move the stand-in C_B values across
    any threshold (CONFIRM_R1B.md).

Frozen predictions (card "Confirmatory design"; "-r1b" = must hold under both models):
  C1-r1b  C_B <= 0.3 with room-relabel p < 0.05 (w30, L1, dedup) in >= 3 of #45, #46, #47, #50, under both models. [0.55]
  C2-r1b  median between-room separation F >= 5 -> C_B < 0.3, F <= 3 -> C_B > 0.3, in every target with F outside
          (3, 5) (>= 1 such target), under both models.                                                    [0.45]
  C3-r1b  NE15 (03-16 split), #35 partition: r_X(#34d) >= 0.7 and DiD = r_X(#35) - r_X(#34d) <= -0.4 with
          partition-permutation p < 0.05, under both models.                                                [0.5]
  C4-r1b  #46 kickoff: |L| cohort-relabel p >= 0.05 and both cohorts' median first post-kickoff shift >= 0.5,
          under both models.                                                                                [0.5]
  C5-r1b  #showcase-live opening (2026-06-11, inside #46): R1_swarm z < 3 and R1_loc >= 2 within +-1 day, both models. [0.25]
Credences are lowered by about 0.05 from confirm.py because each criterion now needs two models to agree.

Reuse disclosure: #45 (H02, H04 activity runs) and #46-#50 (H04, NE21+NE23) carry executed activity runs (other
modality); H26's unrun confirm targets #46/#47 with a close content statistic (room excess): whichever runs second
treats its C1 as non-independent. #34 (C3's pre side): H05's executed NE12/#34 run (activity). NE15: no other user.

Safeguards: refuses to run on the holdout without --confirm --i-understand-this-uses-the-locked-holdout; refuses unless
this script, the card, h47lib.py, explore.py and scheme/build.py are tracked and unmodified. --dry-run uses non-holdout
stand-ins (C1/C2: #41, #42, #44; C3: #40 -> #41; C4: #42 kickoff; C5: 2026-05-11), asserts no holdout day is loaded,
checks that the in-memory builder with ROUND-1 inputs reproduces explore.py's C_B for #41 and #44 within 0.01, then runs
the corrected inputs under both models.

Usage: uv run python hypotheses/H47-room-coherence-length/analysis/confirm_r1b.py --dry-run
       uv run python hypotheses/H47-room-coherence-length/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h47lib as L  # noqa: E402  (thread caps)

_spec = importlib.util.spec_from_file_location("h47explore", HERE / "explore.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)
sys.path.insert(0, str(L.ROOT / "infra/shared"))
import holdout_ledger as HL  # noqa: E402
from common import holdout_mask, load_whitener  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HYP = "H47"
SH, ED = L.SH, L.SH / "embeddings"
FILES = [HERE / "confirm_r1b.py", L.HYP / "README.md", HERE / "h47lib.py", HERE / "explore.py", L.HYP / "scheme/build.py"]
TARGETS_C1 = [45, 46, 47, 50]
STANDINS_C1 = [41, 42, 44]
MODELS = {"bge": {"raw": ("chat_bge_small.npy", "intentions_bge_small.npy"), "goal": "goal_vectors.npy",
                  "agent_day": "agent_day_vec.npy", "white": None},
          "gte": {"raw": ("chat_gte_modernbert.npy", "intentions_gte_modernbert.npy"), "goal": "goal_vectors_gte_modernbert.npy",
                  "agent_day": "agent_day_vec_gte_modernbert.npy", "white": "whitening_gte_modernbert_{}.npz"}}
LEDGER = {"targets": ["G45", "G46", "G47", "G50", "G34", "NE15"], "modality": "message content", "family": ["content_alignment"]}


def whitener(model, regime):
    if MODELS[model]["white"] is None:
        return load_whitener(str(regime), 32)
    z = np.load(ED / MODELS[model]["white"].format(regime))
    mu, U, w = z["mean"], z["components"][:, :32], z["eigenvalues"][:32]
    return lambda x: ((np.asarray(x, dtype=np.float32) - mu) @ U) / np.sqrt(w)


def committed_and_clean():
    for f in FILES:
        rel = str(f.relative_to(L.ROOT))
        tracked = subprocess.run(["git", "-C", str(L.ROOT), "ls-files", "--error-unmatch", rel], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", rel], capture_output=True, text=True).stdout.strip()
        if not tracked or dirty:
            return False, rel
    return True, None


def ledger_gate():
    rep, bad = {}, []
    for t in LEDGER["targets"]:
        r = HL.check(HYP, t, LEDGER["modality"], LEDGER["family"])
        same = sorted({x["hypothesis"] for x in r["prior_runs_same_family"] if x["modality"] == LEDGER["modality"]})
        rep[t] = {"allowed": r["allowed"], "same_family_same_modality_runs": same,
                  "prior_runs": sorted({x["hypothesis"] for x in r["prior_runs"]}),
                  "competing_planned": sorted({x["hypothesis"] for x in r["competing_planned"]})}
        if same:
            bad.append(t)
    return rep, bad


class CData:
    """explore.Data stand-in built in memory. inputs: 'r1' (round-1 outages + own bge dedup; reproduction check only)
    or 'r1b' (outages_fixed + statement_flags). model: 'bge' or 'gte'. Holdout days only when allow_holdout."""

    def __init__(self, goals, allow_holdout, inputs="r1b", model="bge"):
        self.model = model
        cal = pl.read_parquet(SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String)).sort("pt_date")
        hm = dict(zip(cal["pt_date"].to_list(), holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())))
        self.cal = cal
        pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("goal_no").is_in(goals))
        pu = pu.with_columns(pl.col("rooms").list.len().alias("n_rooms_struct"), (pl.col("rooms").list.len() >= 2).alias("multiroom"))
        self.units = pu
        day2unit = {}
        for u, days in pu.select("unit_id", "days").iter_rows():
            for d in days:
                day2unit.setdefault(d, u)
        days = sorted(day2unit)
        if not allow_holdout:
            assert not any(hm.get(d, True) for d in days), "dry run touched a holdout day"
        cc = set(pl.read_parquet(SH / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list())
        st = pl.read_parquet(ED / "statements.parquet").with_row_index("st_row").filter(pl.col("pt_date").is_in(days) & ~pl.col("agent").is_in(list(cc)))
        st = st.with_columns(pl.col("pt_date").replace_strict(day2unit, default=None).alias("unit_id"))
        rt = pl.read_parquet(SH / "rooms_timeline.parquet")
        asof = st.select("st_row", "agent", "t").sort("t").join_asof(rt.select("agent", "room", pl.col("t_start").alias("t")).sort("t"), on="t", by="agent", strategy="backward")
        st = st.join(asof.select("st_row", pl.col("room").alias("room_tl")), on="st_row", how="left")
        st = st.with_columns(pl.coalesce(pl.col("room").cast(pl.Int8), pl.col("room_tl").cast(pl.Int8)).alias("room")).drop("room_tl").sort("st_row")
        n = st.height
        kind = st["kind"].to_numpy(); src = st["src_row"].to_numpy().astype(np.int64)
        dim = 384 if model == "bge" else 768
        raw = np.zeros((n, dim), np.float32)
        for name, fn in zip(("chat", "intent"), MODELS[model]["raw"]):
            m = kind == name
            arr = np.load(ED / fn, mmap_mode="r")
            o = np.argsort(src[m]); tmp = np.empty((m.sum(), dim), np.float32); tmp[o] = np.asarray(arr[src[m][o]], np.float32); raw[m] = tmp
        V = np.zeros((n, 32), np.float32)
        reg = st["regime"].to_numpy()
        for r in np.unique(reg):
            V[reg == r] = whitener(model, r)(raw[reg == r])
        V /= np.clip(np.linalg.norm(V, axis=1, keepdims=True), 1e-9, None)
        if inputs == "r1":   # round-1 rule: raw bge cosine > 0.95 to an earlier own chat statement that PT day
            assert model == "bge"
            rn = raw / np.clip(np.linalg.norm(raw, axis=1, keepdims=True), 1e-9, None)
            tt = st["t"].dt.epoch("us").to_numpy()
            dup = np.zeros(n, bool)
            for idx in st.with_row_index("i").filter(pl.col("kind") == "chat").group_by("agent", "pt_date").agg(pl.col("i"))["i"].to_list():
                idx = np.asarray(idx); idx = idx[np.argsort(tt[idx], kind="stable")]
                if len(idx) >= 2:
                    dup[idx[(np.tril(rn[idx] @ rn[idx].T, -1) > 0.95).any(1)]] = True
            st = st.with_columns(pl.Series("dup", dup), pl.lit(False).alias("dup_copies"))
            odir = SH
        else:
            fl = pl.read_parquet(SH / "statement_flags.parquet", columns=["srow", "self_repeat_bge", "self_repeat_gte", "self_repeat_both"])
            st = st.join(fl, left_on="st_row", right_on="srow", how="left", maintain_order="left")
            chat = pl.col("kind") == "chat"
            st = st.with_columns((chat & (pl.col("self_repeat_bge") | pl.col("self_repeat_gte")).fill_null(False)).alias("dup"),
                                 (chat & pl.col("self_repeat_both").fill_null(False)).alias("dup_copies")
                                 ).drop("self_repeat_bge", "self_repeat_gte", "self_repeat_both")
            odir = SH / "outages_fixed"
        outg = pl.read_parquet(odir / "outages.parquet").filter(pl.col("village_off"))
        sm = pl.read_parquet(odir / "stall_minutes.parquet", columns=["pt_date", "t", "outage_id"]).filter(pl.col("outage_id").is_in(outg["outage_id"].to_list()) & pl.col("pt_date").is_in(days))
        sm = sm.join(cal.select("pt_date", "win_start"), on="pt_date").with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 1800).cast(pl.Int16).alias("win30"))
        voff = sm.group_by("pt_date", "win30").len().filter(pl.col("len") >= 15).select("pt_date", "win30", pl.lit(True).alias("voff"))
        st = st.join(voff, on=["pt_date", "win30"], how="left", maintain_order="left").with_columns(pl.col("voff").fill_null(False))
        self.st = st.with_row_index("sid").with_columns(pl.lit(None, pl.Int8).alias("room_assigned"))
        self.st_restate = self.st
        self.raw = raw
        self.V = V; self.Vs = V
        gl = pl.read_parquet(ED / "goals.parquet"); gv = np.load(ED / MODELS[model]["goal"]).astype(np.float32)
        self.static = {}
        for u, g, regime in pu.select("unit_id", "goal_no", "regime").iter_rows():
            rows = gl.filter((pl.col("goal_no") == g) & pl.col("kind").is_in(["goal", "kickoff", "kickoff_room"]))
            self.static[f"all_{u}"] = L.orthobasis(whitener(model, regime)(gv[rows["gid"].to_numpy()])) if rows.height else np.zeros((0, 32))
        ch = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "pt_date", "speaker_kind", "agent"]).filter((pl.col("speaker_kind") == "agent") & pl.col("pt_date").is_in(days))
              .join(pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"]), on="message_id")
              .with_columns(pl.col("pt_date").replace_strict(day2unit, default=None).alias("unit_id")))
        me = ch.select("unit_id", pl.col("agent").alias("s"), pl.col("mentions_roster").alias("d")).explode("d").filter(pl.col("d").is_not_null() & (pl.col("d") != pl.col("s")))
        me = me.with_columns(pl.min_horizontal("s", "d").alias("a"), pl.max_horizontal("s", "d").alias("b")).group_by("unit_id", "a", "b").len()
        self.mw = {}
        for u, a, b, w in me.iter_rows():
            self.mw.setdefault(u, {})[(int(a), int(b))] = float(w)

    def use_dedup(self, which):
        """'restate' (primary) or 'copies' (sensitivity): swaps the dup column read by explore.build_panel."""
        self.st = self.st_restate if which == "restate" else self.st_restate.with_columns(pl.col("dup_copies").alias("dup"))

    def unit_ids(self, g, multi_only=True):
        u = self.units.filter(pl.col("goal_no") == g).sort("seq")
        if multi_only:
            u = u.filter(pl.col("multiroom"))
        return u["unit_id"].to_list()


def separation_F(D, g):
    units = D.unit_ids(g)
    st = D.st.filter(pl.col("unit_id").is_in(units) & ~pl.col("dup") & ~pl.col("voff") & pl.col("room").is_in([2, 3]))
    Fs = []
    for d in sorted(st["pt_date"].unique().to_list()):
        ga = st.filter(pl.col("pt_date") == d).group_by("agent").agg(pl.col("sid"), pl.col("room").mode().sort().first().alias("room"), pl.len().alias("n")).filter(pl.col("n") >= 3)
        rr = ga["room"].to_numpy()
        if ga.height < 4 or min((rr == 2).sum(), (rr == 3).sum()) < 2:
            continue
        X = np.array([D.V[np.asarray(ix)].mean(0) for ix in ga["sid"].to_list()])
        a, b = X[rr == 2], X[rr == 3]
        sa = ((a - a.mean(0)) ** 2).sum() / max(len(a) - 1, 1); sb = ((b - b.mean(0)) ** 2).sum() / max(len(b) - 1, 1)
        Fs.append(float(((a.mean(0) - b.mean(0)) ** 2).sum() / (sa / len(a) + sb / len(b))))
    return float(np.median(Fs)) if Fs else np.nan


def leadership(D, g, rng):
    cal = D.cal
    days_all = cal["pt_date"].to_list(); goal_of = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    d0 = min(D.units.filter(pl.col("goal_no") == g)["first_day"].to_list())
    i0 = days_all.index(d0)
    pre = days_all[i0 - 1]; post = [d for d in days_all[i0 + 1:i0 + 3] if goal_of[d] == g]
    kk = pl.read_parquet(SH / "kicks_classified.parquet").filter((pl.col("kind") == "human_message") & (pl.col("subkind") == "kickoff") & (pl.col("goal_no") == g)).group_by("room").agg(pl.col("t").min())
    kick = dict(kk.iter_rows())
    if 2 not in kick or 3 not in kick:
        return dict(skipped="kickoff not in both rooms", pass_=None)
    s = D.st.filter(~pl.col("dup"))
    s0 = s.filter(pl.col("pt_date") == d0)
    coh = {int(a): (0 if r == 2 else 1) for a, r in s0.group_by("agent").agg(pl.col("room").mode().sort().first()).iter_rows() if r in (2, 3)}
    s0 = s0.filter(pl.col("agent").is_in(list(coh)))
    kt = {0: kick[2], 1: kick[3]}
    tau = np.array([(t - kt[coh[int(a)]]).total_seconds() / 60 for t, a in zip(s0["t"].to_list(), s0["agent"].to_list())])
    keep = tau >= 0
    raw = D.raw
    spre = s.filter((pl.col("pt_date") == pre) & pl.col("agent").is_in(list(coh)))
    spost = s.filter(pl.col("pt_date").is_in(post) & pl.col("agent").is_in(list(coh)))
    if spre.height == 0:
        return dict(skipped="pre day not loaded (outside the built goals)", pass_=None)
    ev = dict(tau=tau[keep], X=raw[s0["sid"].to_numpy()][keep], agent=s0["agent"].to_numpy()[keep], Xpre=raw[spre["sid"].to_numpy()],
              apre=spre["agent"].to_numpy(), Xpost=raw[spost["sid"].to_numpy()], apost=spost["agent"].to_numpy(), coh=coh)
    r = L.lead_test(ev, rng, n_perm=500, n_boot=0)
    pre_m = L.cohort_means(ev["apre"], ev["Xpre"], coh); post_m = L.cohort_means(ev["apost"], ev["Xpost"], coh)
    yf = {}
    for c in (0, 1):
        dl = post_m[c] - pre_m[c]; vals = []
        for a in [a for a, v in coh.items() if v == c]:
            m = np.flatnonzero(ev["agent"] == a)
            if m.size:
                j = m[np.argmin(ev["tau"][m])]
                vals.append(float((ev["X"][j] - pre_m[c]) @ dl / (dl @ dl)))
        yf[c] = float(np.median(vals)) if vals else np.nan
    return dict(goal=g, L=r["obs"]["L"], p_L=r["p_L"], y_first=yf, pass_=bool(r["p_L"] >= 0.05 and min(yf.values()) >= 0.5))


def detector_day(day, allow_holdout, rng, model):
    cal = pl.read_parquet(SH / "calendar.parquet").sort("pt_date")
    days = cal["pt_date"].to_list(); hol = dict(zip(days, cal["holdout"].to_list()))
    ad = pl.read_parquet(ED / "agent_day.parquet"); av = np.load(ED / MODELS[model]["agent_day"]).astype(np.float32)
    mu = av[ad.filter(~pl.col("holdout"))["gid"].to_numpy()].mean(0)
    use = days if allow_holdout else [d for d in days if not hol[d]]
    ad = ad.filter(pl.col("pt_date").is_in(use))
    mbar = {}
    for (d,), g in ad.group_by(["pt_date"]):
        x = av[g["gid"].to_numpy()] - mu; x /= np.clip(np.linalg.norm(x, axis=1, keepdims=True), 1e-9, None); mbar[d] = x.mean(0)
    seq = [d for d in use if d in mbar]
    r1 = np.array([np.nan] + [L.r1_shift(mbar[seq[i]], mbar[seq[i - 1]]) for i in range(1, len(seq))])
    z = E.trailing_z(r1)
    i = seq.index(day)
    win = [seq[j] for j in (i - 1, i, i + 1) if 0 <= j < len(seq)]
    chd = pl.read_parquet(SH / "chat_core.parquet", columns=["pt_date", "speaker_kind", "agent", "room"]).filter((pl.col("speaker_kind") == "agent") & pl.col("pt_date").is_in(use))
    rm = {(a, d): r for a, d, r in chd.group_by("agent", "pt_date").agg(pl.col("room").mode().sort().first()).select("agent", "pt_date", "room").iter_rows()}
    cc = set(pl.read_parquet(SH / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list())
    vec = {}
    for gid, a, d in ad.select("gid", "agent", "pt_date").iter_rows():
        if a in cc:
            continue
        x = av[gid] - mu; vec.setdefault(d, {})[a] = x / max(np.linalg.norm(x), 1e-9)
    loc = {}
    for d in win:
        j = seq.index(d)
        if j == 0:
            continue
        dp = seq[j - 1]
        common = sorted(set(vec.get(d, {})) & set(vec.get(dp, {})))
        if len(common) < 3:
            continue
        rd = np.array([rm.get((a, d), -1) for a in common]); rp = np.array([rm.get((a, dp), -1) for a in common])
        loc[d], _ = L.r1_loc(np.array([vec[d][a] for a in common]), np.array([vec[dp][a] for a in common]), rd, rp, rng, n_rand=300)
    zz = {d: float(z[seq.index(d)]) for d in win}
    return dict(day=day, R1_swarm_z=zz, R1_loc=loc, pass_=bool(max([v for v in zz.values() if np.isfinite(v)], default=0) < 3 and max([v for v in loc.values() if np.isfinite(v)], default=-9) >= 2))


def run_model(goals_c1, c3_units, c4_goal, c5_day, allow_holdout, model):
    rng = np.random.default_rng(L.SEED + 77)
    allg = sorted(set(goals_c1) | {int(u.rstrip("abcdefgh")) for u in c3_units} | {c4_goal})
    D = CData(allg, allow_holdout, "r1b", model)
    out = {"model": model, "C1": {}, "C1_copies": {}, "C2": {}}
    for g in goals_c1:
        units = D.unit_ids(g)
        D.use_dedup("restate")
        r = E.period_coherence(D, units, "w30", 1, 300, rng)
        F = separation_F(D, g)
        cb = r["obs"]["C_B"] if r else None
        out["C1"][f"#{g}"] = dict(units=units, C_B=cb, p=r.get("p_DB") if r else None,
                                  ok=bool(r and cb <= 0.3 and r["p_DB"] < 0.05))
        out["C2"][f"#{g}"] = dict(F=F, C_B=cb, ok=(None if (cb is None or (3 < F < 5)) else
                                                   bool((F >= 5 and cb < 0.3) or (F <= 3 and cb > 0.3))))
        D.use_dedup("copies")
        rc = E.period_coherence(D, units, "w30", 1, 100, rng)
        out["C1_copies"][f"#{g}"] = dict(C_B=rc["obs"]["C_B"] if rc else None, p=rc.get("p_DB") if rc else None)
        D.use_dedup("restate")
    out["C1_pass"] = sum(v["ok"] for v in out["C1"].values()) >= (3 if len(goals_c1) == 4 else 2)
    c2 = [v["ok"] for v in out["C2"].values() if v["ok"] is not None]
    out["C2_pass"] = bool(c2) and all(c2)
    pre_u, post_u = c3_units
    s = D.st.filter((pl.col("unit_id") == post_u) & ~pl.col("dup"))
    part = {int(a): (0 if r == 2 else 1) for a, r in s.group_by("agent").agg(pl.col("room").mode().sort().first()).iter_rows() if r in (2, 3)}
    Cs = {}
    for u in (pre_u, post_u):
        P = E.build_panel(D, u, "w30")
        Cs[u] = L.contributions(P, *L.deviations(P, 1))
    rx = {u: L.partition_ratio(Cs[u], part)["r_X"] for u in Cs}
    did = rx[post_u] - rx[pre_u]
    nul = []
    for _ in range(1000):
        pp = L.permute_partition(part, rng)
        nul.append(L.partition_ratio(Cs[post_u], pp)["r_X"] - L.partition_ratio(Cs[pre_u], pp)["r_X"])
    nul = np.array(nul, float)
    p3 = float((1 + (nul <= did).sum()) / (1 + np.isfinite(nul).sum()))
    out["C3"] = dict(units=c3_units, r_X=rx, DiD=did, p=p3, pass_=bool(rx[pre_u] >= 0.7 and did <= -0.4 and p3 < 0.05))
    out["C4"] = leadership(D, c4_goal, rng)
    out["C5"] = detector_day(c5_day, allow_holdout, rng, model)
    return out


def combine(res):
    """Both-model rule: a criterion passes only if it passes under bge and gte."""
    b, g = res["bge"], res["gte"]
    c1 = {k: bool(b["C1"][k]["ok"] and g["C1"][k]["ok"]) for k in b["C1"]}
    need = 3 if len(c1) == 4 else 2
    return {"C1-r1b": sum(c1.values()) >= need, "C1-r1b_per_target": c1,
            "C2-r1b": bool(b["C2_pass"] and g["C2_pass"]),
            "C3-r1b": bool(b["C3"]["pass_"] and g["C3"]["pass_"]),
            "C4-r1b": (None if b["C4"].get("pass_") is None or g["C4"].get("pass_") is None else bool(b["C4"]["pass_"] and g["C4"]["pass_"])),
            "C5-r1b": bool(b["C5"]["pass_"] and g["C5"]["pass_"])}


def main():
    OUTC = L.OUT / "confirm"
    OUTC.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    gate, bad = ledger_gate()
    if "--dry-run" in sys.argv:
        # 1) builder check with ROUND-1 inputs (bge): must reproduce explore.py's C_B for #41 and #44
        rng = np.random.default_rng(L.SEED + 77)
        D1 = CData([41, 44], False, "r1", "bge")
        ref = json.loads((L.OUT / "results/coherence.json").read_text())
        repro = {}
        for g in (41, 44):
            r = E.period_coherence(D1, D1.unit_ids(g), "w30", 1, 0, rng)
            a, b = r["obs"]["C_B"], ref[f"G{g}"]["w30"]["obs"]["C_B"]
            assert abs(a - b) < 0.01, f"builder does not reproduce explore C_B for #{g}: {a} vs {b}"
            repro[f"#{g}"] = [a, b]
        del D1
        # 2) corrected inputs, both models
        res = {m: run_model(STANDINS_C1, ("40", "41"), 42, "2026-05-11", False, m) for m in MODELS}
        out = {"mode": "dry-run r1b (non-holdout stand-ins)", "repro_round1_inputs_bge": repro, "ledger": gate,
               "models": res, "scores": combine(res), "secs": round(time.time() - t0, 1)}
        L.jdump(out, OUTC / "confirm_r1b_dryrun.json")
        print(json.dumps({"repro": repro, "scores": out["scores"], "ledger_blocked": bad,
                          "C1": {m: {k: (v["C_B"], v["p"]) for k, v in res[m]["C1"].items()} for m in res},
                          "C1_copies": {m: {k: v["C_B"] for k, v in res[m]["C1_copies"].items()} for m in res},
                          "C2_F": {m: {k: v["F"] for k, v in res[m]["C2"].items()} for m in res},
                          "C3": {m: [res[m]["C3"]["r_X"], res[m]["C3"]["DiD"], res[m]["C3"]["p"]] for m in res},
                          "C4": {m: res[m]["C4"] for m in res},
                          "C5": {m: [res[m]["C5"]["R1_swarm_z"], res[m]["C5"]["R1_loc"]] for m in res},
                          "secs": out["secs"]}, default=str, indent=1))
        return
    if not ("--confirm" in sys.argv and "--i-understand-this-uses-the-locked-holdout" in sys.argv):
        sys.exit("Refusing: confirmatory run on the locked holdout needs --confirm --i-understand-this-uses-the-locked-holdout")
    ok, badf = committed_and_clean()
    if not ok:
        sys.exit(f"Refusing: {badf} is not committed or has uncommitted changes (holdout reuse policy, item 1)")
    if bad:
        sys.exit(f"Refusing: same-family same-modality prior run on {bad} (holdout ledger); needs Vivian's ruling")
    print("Ledger gate:", json.dumps(gate, indent=1))
    res = {m: run_model(TARGETS_C1, ("34d", "35"), 46, "2026-06-11", True, m) for m in MODELS}
    out = {"mode": "CONFIRMATORY r1b (locked holdout)", "git_commit": L.git_commit(), "ledger": gate, "models": res,
           "scores": combine(res)}
    L.jdump(out, OUTC / "confirm_r1b.json")
    print(json.dumps(out["scores"], default=str, indent=1))


if __name__ == "__main__":
    main()
