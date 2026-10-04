"""H47 confirmatory script (LOCKED HOLDOUT). Written 2026-10-04 after exploratory round 1. NOT RUN.

Frozen predictions (card "Confirmatory design"):
  C1 coherence length (replication): C_B <= 0.3 with room-relabel p < 0.05 (w30, L1, dedup) in >= 3 of the four
     held-out two-room periods #45, #46, #47, #50.                                                          [0.6]
  C2 post hoc rule, now frozen: in each target, median between-room separation F >= 5 -> C_B < 0.3, and
     F <= 3 -> C_B > 0.3; holds in all targets whose F lies outside (3, 5) (at least one such target needed). [0.5]
  C3 NE15 channel cut (03-16 split): with the #35 partition, r_X(#34d, one room, held out) >= 0.7 and
     DiD = r_X(#35) - r_X(#34d) <= -0.4 with joint partition-permutation p < 0.05.                         [0.55]
  C4 leadership null at the #46 kickoff (both rooms kicked off 16:00 UTC): |L| cohort-relabel p >= 0.05, and
     both cohorts' median first post-kickoff statement shift fraction >= 0.5 (immediate quench).           [0.55]
  C5 detector at the #showcase-live opening (2026-06-11, inside #46): R1_swarm z < 3 and R1_loc >= 2 within
     +-1 day.                                                                                               [0.3]

Reuse disclosure (hypotheses/holdout.md policy): #45 was used by H02 (activity couplings) and is planned by H23 (message
content); #46/#47 are the primary targets of H26's unrun confirm (content room excess: CLOSE to C1's statistic, so
whichever runs second must disclose and treat its C1 as non-independent); #34 (C3's pre side) is targeted by the unrun
confirm scripts of H01, H05, H07, H12, H19, H21; NE15 was used by H05's confirmatory run (talk-activity coupling, a
different modality). Disclose in this card, the other cards and LOG.md before running.

Safeguards:
  * refuses to run on the holdout without --confirm --i-understand-this-uses-the-locked-holdout;
  * refuses unless this script, the card, h47lib.py, explore.py and scheme/build.py are tracked and unmodified in git;
  * --dry-run uses non-holdout stand-ins (C1/C2: #41, #42, #44; C3 analogue: #40 -> #41 with the #41 partition;
    C4: #42 kickoff; C5: the 05-11 split day), asserts that no holdout day is loaded, and checks that the
    in-memory builder reproduces explore.py's C_B for #41 and #44 within 0.01.

Usage: uv run python hypotheses/H47-room-coherence-length/analysis/confirm.py --dry-run
       uv run python hypotheses/H47-room-coherence-length/analysis/confirm.py --confirm --i-understand-this-uses-the-locked-holdout
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h47lib as L  # noqa: E402

_spec = importlib.util.spec_from_file_location("h47explore", HERE / "explore.py")
E = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(E)
sys.path.insert(0, str(L.ROOT / "infra/shared"))
sys.path.insert(0, str(L.ROOT / "hypotheses/H36-reorganization-alarm/analysis"))
from common import holdout_mask, load_whitener  # noqa: E402
from h36lib import trailing_z  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

SH, ED = L.SH, L.SH / "embeddings"
OUTC = L.OUT / "confirm"
FILES = [HERE / "confirm.py", L.HYP / "README.md", HERE / "h47lib.py", HERE / "explore.py", L.HYP / "scheme/build.py"]
TARGETS_C1 = [45, 46, 47, 50]
STANDINS_C1 = [41, 42, 44]


def committed_and_clean():
    for f in FILES:
        rel = str(f.relative_to(L.ROOT))
        tracked = subprocess.run(["git", "-C", str(L.ROOT), "ls-files", "--error-unmatch", rel], capture_output=True).returncode == 0
        dirty = subprocess.run(["git", "-C", str(L.ROOT), "status", "--porcelain", "--", rel], capture_output=True, text=True).stdout.strip()
        if not tracked or dirty:
            return False, rel
    return True, None


class CData:
    """explore.Data stand-in built in memory for the given goal periods (holdout allowed only in confirm mode)."""

    def __init__(self, goals, allow_holdout):
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
        raw = np.zeros((n, 384), np.float32)
        for name, fn in (("chat", "chat_bge_small.npy"), ("intent", "intentions_bge_small.npy")):
            m = kind == name
            arr = np.load(ED / fn, mmap_mode="r")
            o = np.argsort(src[m]); tmp = np.empty((m.sum(), 384), np.float32); tmp[o] = np.asarray(arr[src[m][o]], np.float32); raw[m] = tmp
        V = np.zeros((n, 32), np.float32)
        reg = st["regime"].to_numpy()
        for r in np.unique(reg):
            V[reg == r] = load_whitener(str(r), 32)(raw[reg == r])
        V /= np.clip(np.linalg.norm(V, axis=1, keepdims=True), 1e-9, None)
        rn = raw / np.clip(np.linalg.norm(raw, axis=1, keepdims=True), 1e-9, None)
        tt = st["t"].dt.epoch("us").to_numpy()
        dup = np.zeros(n, bool)
        for idx in st.with_row_index("i").filter(pl.col("kind") == "chat").group_by("agent", "pt_date").agg(pl.col("i"))["i"].to_list():
            idx = np.asarray(idx); idx = idx[np.argsort(tt[idx], kind="stable")]
            if len(idx) >= 2:
                dup[idx[(np.tril(rn[idx] @ rn[idx].T, -1) > 0.95).any(1)]] = True
        outg = pl.read_parquet(SH / "outages.parquet").filter(pl.col("village_off"))
        sm = pl.read_parquet(SH / "stall_minutes.parquet", columns=["pt_date", "t", "outage_id"]).filter(pl.col("outage_id").is_in(outg["outage_id"].to_list()) & pl.col("pt_date").is_in(days))
        sm = sm.join(cal.select("pt_date", "win_start"), on="pt_date").with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 1800).cast(pl.Int16).alias("win30"))
        voff = sm.group_by("pt_date", "win30").len().filter(pl.col("len") >= 15).select("pt_date", "win30", pl.lit(True).alias("voff"))
        st = st.with_columns(pl.Series("dup", dup)).join(voff, on=["pt_date", "win30"], how="left", maintain_order="left").with_columns(pl.col("voff").fill_null(False))
        self.st = st.with_row_index("sid").with_columns(pl.lit(None, pl.Int8).alias("room_assigned"))
        self.raw = raw
        self.V = V; self.Vs = V
        # static fields and mentions per unit
        gl = pl.read_parquet(ED / "goals.parquet"); gv = np.load(ED / "goal_vectors.npy").astype(np.float32)
        self.static = {}
        for u, g, regime in pu.select("unit_id", "goal_no", "regime").iter_rows():
            rows = gl.filter((pl.col("goal_no") == g) & pl.col("kind").is_in(["goal", "kickoff", "kickoff_room"]))
            self.static[f"all_{u}"] = L.orthobasis(load_whitener(str(regime), 32)(gv[rows["gid"].to_numpy()])) if rows.height else np.zeros((0, 32))
        ch = (pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "pt_date", "speaker_kind", "agent"]).filter((pl.col("speaker_kind") == "agent") & pl.col("pt_date").is_in(days))
              .join(pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"]), on="message_id")
              .with_columns(pl.col("pt_date").replace_strict(day2unit, default=None).alias("unit_id")))
        me = ch.select("unit_id", pl.col("agent").alias("s"), pl.col("mentions_roster").alias("d")).explode("d").filter(pl.col("d").is_not_null() & (pl.col("d") != pl.col("s")))
        me = me.with_columns(pl.min_horizontal("s", "d").alias("a"), pl.max_horizontal("s", "d").alias("b")).group_by("unit_id", "a", "b").len()
        self.mw = {}
        for u, a, b, w in me.iter_rows():
            self.mw.setdefault(u, {})[(int(a), int(b))] = float(w)

    def unit_ids(self, g, multi_only=True):
        u = self.units.filter(pl.col("goal_no") == g).sort("seq")
        if multi_only:
            u = u.filter(pl.col("multiroom"))
        return u["unit_id"].to_list()


def separation_F(D, g, rng):
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


def run(goals_c1, c3_units, c4_goal, c5_day, allow_holdout):
    rng = np.random.default_rng(L.SEED + 77)
    allg = sorted(set(goals_c1) | {int(u.rstrip("abcdefgh")) for u in c3_units} | {c4_goal})
    D = CData(allg, allow_holdout)
    out = {"C1": {}, "C2": {}}
    for g in goals_c1:
        units = D.unit_ids(g)
        r = E.period_coherence(D, units, "w30", 1, 300, rng)
        F = separation_F(D, g, rng)
        out["C1"][f"#{g}"] = dict(units=units, C_B=r["obs"]["C_B"] if r else None, p=r.get("p_DB") if r else None,
                                  ok=bool(r and r["obs"]["C_B"] <= 0.3 and r["p_DB"] < 0.05))
        out["C2"][f"#{g}"] = dict(F=F, C_B=out["C1"][f"#{g}"]["C_B"],
                                  ok=(None if (F > 3 and F < 5) else bool((F >= 5 and out["C1"][f"#{g}"]["C_B"] < 0.3) or (F <= 3 and out["C1"][f"#{g}"]["C_B"] > 0.3))))
    out["C1_pass"] = sum(v["ok"] for v in out["C1"].values()) >= (3 if len(goals_c1) == 4 else 2)
    c2 = [v["ok"] for v in out["C2"].values() if v["ok"] is not None]
    out["C2_pass"] = bool(c2) and all(c2)
    # C3: partition from the post unit (two rooms), r_X before (one room) and after
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
    # C4: leadership at c4_goal's kickoff (cohorts = rooms on day 0; pre = previous active day; post = next two)
    out["C4"] = leadership(D, c4_goal, rng)
    # C5: detector on c5_day
    out["C5"] = detector_day(c5_day, allow_holdout, rng)
    return out


def leadership(D, g, rng):
    cal = D.cal if True else None
    days_all = cal["pt_date"].to_list(); goal_of = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    d0 = min(D.units.filter(pl.col("goal_no") == g)["first_day"].to_list())
    i0 = days_all.index(d0)
    pre = days_all[i0 - 1]; post = [d for d in days_all[i0 + 1:i0 + 3] if goal_of[d] == g]
    kk = pl.read_parquet(SH / "kicks_classified.parquet").filter((pl.col("kind") == "human_message") & (pl.col("subkind") == "kickoff") & (pl.col("goal_no") == g)).group_by("room").agg(pl.col("t").min())
    kick = dict(kk.iter_rows())
    if 2 not in kick or 3 not in kick:
        return dict(skipped="kickoff not in both rooms")
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
        return dict(skipped="pre day not loaded (outside the built goals)")
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


def detector_day(day, allow_holdout, rng):
    cal = pl.read_parquet(SH / "calendar.parquet").sort("pt_date")
    days = cal["pt_date"].to_list(); hol = dict(zip(days, cal["holdout"].to_list()))
    ad = pl.read_parquet(ED / "agent_day.parquet"); av = np.load(ED / "agent_day_vec.npy").astype(np.float32)
    mu = av[ad.filter(~pl.col("holdout"))["gid"].to_numpy()].mean(0)
    use = days if allow_holdout else [d for d in days if not hol[d]]
    ad = ad.filter(pl.col("pt_date").is_in(use))
    mbar = {}
    for (d,), g in ad.group_by(["pt_date"]):
        x = av[g["gid"].to_numpy()] - mu; x /= np.clip(np.linalg.norm(x, axis=1, keepdims=True), 1e-9, None); mbar[d] = x.mean(0)
    seq = [d for d in use if d in mbar]
    r1 = np.array([np.nan] + [L.r1_shift(mbar[seq[i]], mbar[seq[i - 1]]) for i in range(1, len(seq))])
    z = trailing_z(r1)
    i = seq.index(day)
    win = [seq[j] for j in (i - 1, i, i + 1) if 0 <= j < len(seq)]
    # R1_loc on the window days from chat rooms (modal room per agent-day)
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


def main():
    OUTC.mkdir(parents=True, exist_ok=True)
    if "--dry-run" in sys.argv:
        out = run(STANDINS_C1, ("40", "41"), 42, "2026-05-11", allow_holdout=False)
        ref = json.loads((L.OUT / "results/coherence.json").read_text())
        for g in (41, 44):
            a, b = out["C1"][f"#{g}"]["C_B"], ref[f"G{g}"]["w30"]["obs"]["C_B"]
            assert abs(a - b) < 0.01, f"builder does not reproduce explore C_B for #{g}: {a} vs {b}"
        out["mode"] = "dry-run (non-holdout stand-ins); reproduces explore C_B for #41, #44 within 0.01"
        L.jdump(out, OUTC / "confirm_dryrun.json")
        print(json.dumps({k: v for k, v in out.items() if k != "C4"}, default=str, indent=1)[:3000])
        print("C4", out["C4"])
        return
    if not ("--confirm" in sys.argv and "--i-understand-this-uses-the-locked-holdout" in sys.argv):
        sys.exit("Refusing: confirmatory run on the locked holdout needs --confirm --i-understand-this-uses-the-locked-holdout")
    ok, bad = committed_and_clean()
    if not ok:
        sys.exit(f"Refusing: {bad} is not committed or has uncommitted changes (holdout reuse policy, item 1)")
    out = run(TARGETS_C1, ("34d", "35"), 46, "2026-06-11", allow_holdout=True)
    out["mode"] = "CONFIRMATORY (locked holdout)"; out["git_commit"] = L.git_commit()
    L.jdump(out, OUTC / "confirm.json")
    print(json.dumps(out, default=str, indent=1)[:4000])


if __name__ == "__main__":
    main()
