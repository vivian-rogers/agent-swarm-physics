"""H28 confirmatory test on the locked holdout (#22, #28, #45), RE-FROZEN ON ROUND-1B INPUTS. WRITTEN, NOT RUN.

Re-freeze of `confirm_holdout.py` (left byte-for-byte untouched), written 2026-10-04 before any holdout data was read.
What changed is listed in `CONFIRM_R1B.md`. In short:
  * visibility: t_vis = t_call of the recipient's ledger receiving call (DQ1 `context_ledger_items` x `call_windows`),
    and the link time-shift null re-derives t_vis from receiving calls (round 1b `H28_DATA=r1b`), instead of the
    first-logged-turn rule (event turns before NE09);
  * a new in-flight placebo R4-r1b (blind window (t_post, t_vis] vs read window, round-1b NE09 native);
  * a descriptive work-switch variant on DQ4 agent work commits (`H28_TOUCH=work`), reported, not scored.
Activity, outages and embeddings are not inputs of H28 (active bins come from logged turns), so DQ8 trim and
`activity_bins_fixed` do not apply.

  uv run python hypotheses/H28-links-spread-herding/analysis/confirm_r1b.py --dry-run [--check-builder DIR]
      frozen pipeline on non-holdout stand-ins (#31 for #22, #30 for #28, #41 for #45) from the existing round-1b
      folders; --check-builder rebuilds the stand-ins' ledger exposures with this script's builder into DIR and
      compares them with r1b/G<NN>/. Touches no holdout data. Also prints the holdout-ledger reuse status (no data).
  uv run python hypotheses/H28-links-spread-herding/analysis/confirm_r1b.py --confirm --i-understand-this-uses-the-locked-holdout
      builds round-1 + round-1b scheme folders for the held-out periods into data/processed/H28-links-spread-herding/
      confirm_r1b/ and applies the rule below. Refuses unless this script, CONFIRM_R1B.md, the card and the code it
      imports are committed and unmodified, and unless infra/shared/holdout_ledger.check() allows every target.

Reuse disclosure (hypotheses/holdout.md; ledger L173-L175): H02 and H04 ran #45 on activity timing (other modality).
H11 (project-label co-occupancy), H27, H06, H08, H15, H18, H23 and H34 plan uses of the same targets. H28's statistic
(lagged link exposure -> arrival hazard against a link time-shift null, lead and in-flight placebos) is different and
unexamined on these periods; whoever runs second must disclose in both cards and LOG.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ["H28_DATA"] = "r1b"                 # ledger visibility + receiving-call shift null (round 1b switch)
os.environ.pop("H28_TOUCH", None)              # primary outcome: attention touches (as frozen); work is a variant
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("POLARS_MAX_THREADS", "2")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h28core as hc  # noqa: E402
from h28lib import OUT, ROOT, SHARED, gname, held_goals  # noqa: E402

TARGETS = {22: dict(standin=31, rooms=1), 28: dict(standin=30, rooms=1), 45: dict(standin=41, rooms=2)}
HYP = "H28"
READ_MS = 15 * 60_000

# ---- Frozen decision rule (re-frozen 2026-10-04 on round-1b inputs, before any holdout data was read) ---------------
FROZEN = dict(
    shifts=99, alpha=0.05, z_shift=2.0, boot=2000, min_work_arrivals=30,
    inputs="H28_DATA=r1b: ledger receiving-call t_vis; shift null re-derives t_vis from receiving calls",
    # Original claim (unchanged from confirm_holdout.py):
    # C1 (per target): kappa > 0, cluster-robust p < 0.05 and z_shift >= 2
    # C2 (common drive): kappa - kappa_lead > 0, one-sided p < 0.05, in >= 2 of 3 targets
    # C3 (room placebo, where a second room has links): kappa_other < kappa_same and kappa_other's 95% CI contains 0
    # C4 (branching): R_link < 0.5 in every target
    # CONFIRMED if C1 in >= 2/3 and C2, C3, C4 hold; REFUTED if C1 fails (kappa <= 0 or z_shift < 2) in >= 2/3;
    # otherwise INCONCLUSIVE.
    # Round-1 pattern (co-burst reading), unchanged:
    # R1 kappa > 0 with p < 0.05 in >= 2/3; R2 kappa_lead >= kappa (joint model) in >= 2/3; R3 R_link in [0.05, 0.45]
    # in every target. PATTERN HOLDS if R1-R3 hold; FAILS if R2 fails in >= 2/3.
    # NEW R4-r1b (in-flight placebo; round-1b NE09 native rule N9b, STANDARDS impostor 4): pooled over the three
    # targets, E_blind (switch rate in (t_post, t_vis] / shift-null rate) has 90% cluster-bootstrap lower bound > 1
    # and E_blind >= 0.5 * E_read (read window (t_vis, t_vis + 15 min]). HOLDS -> switches start before the link
    # can be read (links mark bursts). Reported as its own verdict line; it does not change CLAIM or PATTERN.
    # W-r1b (descriptive): kappa_work, z_shift, kappa_lead on DQ4 work-commit arrivals where >= 30 work arrivals.
    # Expectation (round 1b: P1 5/11, lead >= lag 9/11, E_blind 6.5 vs E_read 3.5): CLAIM REFUTED or INCONCLUSIVE;
    # PATTERN HOLDS; R4-r1b HOLDS. Unchanged from round 1 for CLAIM and PATTERN.
)


def committed_clean(paths) -> bool:
    for p in paths:
        r = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", str(p)], capture_output=True)
        if r.returncode != 0:
            return False
        r = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "HEAD", "--", str(p)])
        if r.returncode != 0:
            return False
    return True


def ledger_status(strict: bool) -> bool:
    """infra/shared/holdout_ledger.check() for every target with this hypothesis's own ledger modality/families.
    Reads the ledger only (no data). strict: return False if any target is not allowed."""
    sys.path.insert(0, str(ROOT))
    from infra.shared import holdout_ledger as hl
    led = hl.load()
    ok = True
    for g in TARGETS:
        t = f"G{g:02d}"
        mine = [e for e in led["entries"] if e["hypothesis"] == HYP and e["target"] == t]
        mod = mine[0]["modality"] if mine else "project labels"
        fam = sorted({f for e in mine for f in e["estimator_family"]})
        r = hl.check(HYP, t, mod, fam)
        print(f"ledger {t}: allowed={r['allowed']} needs_disclosure={r['needs_disclosure']} "
              f"prior_runs={sorted({u['hypothesis'] for u in r['prior_runs']})} "
              f"same_family_runs={sorted({u['hypothesis'] for u in r['prior_runs_same_family']})} "
              f"competing_planned={sorted({u['hypothesis'] for u in r['competing_planned']})}")
        ok &= r["allowed"]
    return ok or not strict


# ---- round-1b scheme for one period (mirror of scheme/build_r1b.py: build(), with the holdout assertion lifted only
#      when called from the guarded --confirm path) -------------------------------------------------------------------
def build_r1b_period(g: int, src_root: Path, allow_holdout: bool):
    import datetime as _dt
    src = src_root / gname(g)
    meta = json.loads((src / "meta.json").read_text())
    days = meta["days"]
    roster = pl.read_parquet(SHARED / "roster.parquet")
    cc = set(roster.filter(pl.col("claude_code"))["agent"].to_list())
    chat_ids = pl.read_parquet(SHARED / "chat_core.parquet", columns=["message_id"]).with_row_index("msg").select(
        pl.col("msg").cast(pl.UInt32), "message_id")
    items = pl.scan_parquet(SHARED / "context_ledger_items.parquet").select("turn_id", "message_id")
    cw = pl.scan_parquet(SHARED / "call_windows.parquet").select("turn_id", "agent", "t_call", "ctx_mode", "holdout")
    wc = pl.scan_parquet(SHARED / "work_commits.parquet").filter(
        pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent") & ~pl.col("automated")
        & pl.col("author_agent").is_not_null()).select("repo", "t", "author_agent", "holdout")
    t0 = _dt.datetime.fromtimestamp(days[0]["ws_ms"] / 1000 - 7200, _dt.timezone.utc)
    t1 = _dt.datetime.fromtimestamp(days[-1]["we_ms"] / 1000 + 26 * 3600, _dt.timezone.utc)
    links = pl.read_parquet(src / "links.parquet")
    lm = links.select("msg", "sender").unique("msg").join(chat_ids, on="msg", how="left")
    assert lm["message_id"].null_count() == 0
    calls = cw.filter((pl.col("t_call") >= t0) & (pl.col("t_call") <= t1)).collect()
    if not allow_holdout:
        calls = calls.filter(~pl.col("holdout"))
    it = items.join(lm.lazy().select("message_id", "msg", "sender"), on="message_id", how="inner").collect()
    ex = it.join(calls.select("turn_id", "agent", "t_call", "holdout"), on="turn_id", how="inner")
    if not allow_holdout:
        assert not ex["holdout"].any(), "holdout ledger row"
    ex = ex.filter((pl.col("agent").cast(pl.Int16) != pl.col("sender")) & ~pl.col("agent").is_in(list(cc)))
    exposures = (ex.group_by("msg", "agent").agg(pl.col("t_call").min())
                 .select(pl.col("msg").cast(pl.UInt32), pl.col("agent").cast(pl.Int8).alias("recipient"),
                         pl.col("t_call").dt.epoch("ms").alias("t_vis_ms")).sort("msg", "recipient"))
    rc = (calls.filter(pl.col("ctx_mode").cast(pl.String) != "summary")
          .select(pl.col("agent").cast(pl.Int8), pl.col("t_call").dt.epoch("ms").alias("t_ms")).sort("agent", "t_ms"))
    uni = [u["project"] for u in meta["universe"]]
    w = (wc.filter(pl.col("repo").cast(pl.String).is_in(uni)).collect()
         .with_columns(pl.col("t").dt.epoch("ms").alias("t_ms")))
    if not allow_holdout:
        w = w.filter(~pl.col("holdout"))
    dws = np.array([d["ws_ms"] for d in days]); dwe = np.array([d["we_ms"] for d in days])
    tm = w["t_ms"].to_numpy()
    k = np.clip(np.searchsorted(dws, tm, "right") - 1, 0, len(dws) - 1)
    w = w.filter(pl.Series((tm >= dws[k]) & (tm <= dwe[k])))
    tw = w.select(pl.col("author_agent").alias("agent").cast(pl.Int8), "t_ms", pl.col("repo").cast(pl.String).alias("project"),
                  pl.lit(2, pl.Int8).alias("source")).filter(~pl.col("agent").is_in(list(cc))).sort("t_ms")
    return dict(exposures=exposures, calls=rc, touches_work=tw)


def write_r1b(parts: dict, dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    for name, df in parts.items():
        df.write_parquet(dest / f"{name}.parquet", compression="zstd", compression_level=9)


# ---- statistics ---------------------------------------------------------------------------------------------------
def evaluate(P, seed=0, work=False):
    """Frozen per-target statistics (identical to confirm_holdout.evaluate) on the loaded period P."""
    from scipy.stats import norm
    rng = np.random.default_rng(seed)
    R, B, G = hc.build_rows(P)
    P["_B"] = B
    F = hc.link_features(P, R)
    res = hc.fit(R, F, "primary")
    k, se = hc.coef(res, "E60")
    null = []
    for _ in range(FROZEN["shifts"]):
        lt, tv = hc.shift_links(P, rng)
        null.append(hc.coef(hc.fit(R, hc.link_features(P, R, link_t=lt, t_vis=tv), "primary"), "E60")[0])
    null = np.array([v for v in null if np.isfinite(v)])
    z = (k - null.mean()) / null.std(ddof=1)
    p = 2 * norm.sf(abs(k / se))
    rl = hc.fit(R, F, "lead")
    i, j = rl["names"].index("E60"), rl["names"].index("lead60")
    d = rl["beta"][i] - rl["beta"][j]
    vd = rl["V"][i, i] + rl["V"][j, j] - 2 * rl["V"][i, j]
    out = dict(kappa=k, se=se, p=p, z_shift=z, diff_lead=d, p_diff_lead=float(norm.sf(d / np.sqrt(vd))),
               kappa_joint=float(rl["beta"][i]), kappa_lead=float(rl["beta"][j]),
               arrivals=int(R["y"].sum()), links=int((P["links"]["x"] >= 0).sum()))
    if work:
        return out
    out["C1"] = bool(k > 0 and p < FROZEN["alpha"] and z >= FROZEN["z_shift"])
    out["C2"] = bool(d > 0 and out["p_diff_lead"] < FROZEN["alpha"])
    if F["other60"].sum() > 0:
        rr = hc.fit(R, F, "room")
        ko, so = hc.coef(rr, "other60")
        ks, _ = hc.coef(rr, "E60")
        out.update(kappa_other=ko, se_other=so, kappa_same=ks, C3=bool(ko < ks and abs(ko / so) < 1.96))
    att = hc.attributable(res, R, F, hc.count_exposures(P), link_names=("E60",), draws=0)
    out.update(lam=att["lam"], R_link=att["R_link"], C4=bool(att["R_link"] < 0.5))
    out["R1"] = bool(k > 0 and p < FROZEN["alpha"])
    out["R2"] = bool(out["kappa_lead"] >= out["kappa_joint"])
    out["R3"] = bool(0.05 <= att["R_link"] <= 0.45)
    return out


def blind_window(P, seed):
    """R4-r1b inputs: per (link, susceptible recipient) pair, switches in the blind and read windows, and the
    shift-null rates (round-1b NE09 native, r1b_natives.pair_counts)."""
    import r1b_natives as rn
    tcomp, acomp = rn.arrivals(P)
    tcomp = np.sort(tcomp)
    obs = rn.pair_counts(P, P["links"]["t"], P["expo"]["t_vis"], tcomp, acomp)
    rng = np.random.default_rng(2809 + seed)
    rb, rr = [], []
    for _ in range(FROZEN["shifts"]):
        lt, tv = hc.shift_links(P, rng)
        c = rn.pair_counts(P, lt, tv, tcomp, acomp)
        rb.append(c["nb"].sum() / max(c["db"].sum(), 1e-9)); rr.append(c["nr"].sum() / max(len(c["nr"]) * 15.0, 1e-9))
    return obs, float(np.mean(rb)), float(np.mean(rr))


def pool_blind(rows, seed=28):
    """Pooled E_blind, E_read over targets: sum observed / sum expected; cluster bootstrap over link messages."""
    rng = np.random.default_rng(seed)

    def stat(sel):
        ob = sum(o["nb"][s].sum() for (o, _, _), s in zip(rows, sel)); eb = sum(rb * o["db"][s].sum() for (o, rb, _), s in zip(rows, sel))
        orr = sum(o["nr"][s].sum() for (o, _, _), s in zip(rows, sel)); er = sum(rr * 15.0 * len(o["nr"][s]) for (o, _, rr), s in zip(rows, sel))
        return (ob / eb if eb > 0 else np.nan), (orr / er if er > 0 else np.nan)
    Eb, Er = stat([np.arange(len(o["nb"])) for o, _, _ in rows])
    bs = []
    for _ in range(FROZEN["boot"]):
        sel = []
        for o, _, _ in rows:
            u, inv = np.unique(o["lid"], return_inverse=True)
            cnt = np.bincount(rng.integers(0, len(u), len(u)), minlength=len(u))
            sel.append(np.repeat(np.arange(len(inv)), cnt[inv]))
        bs.append(stat(sel))
    bs = np.array(bs, float)
    lo = float(np.nanquantile(bs[:, 0], 0.05))
    return dict(E_blind=float(Eb), E_blind_lo90=lo, E_read=float(Er),
                R4_r1b=bool(lo > 1 and Eb >= 0.5 * Er))


def decide(per, blind):
    n = len(per)
    c1 = sum(v["C1"] for v in per.values())
    c2 = sum(v["C2"] for v in per.values()) >= 2
    c3 = all(v.get("C3", True) for v in per.values())
    c4 = all(v["C4"] for v in per.values())
    fail = sum((v["kappa"] <= 0) or (v["z_shift"] < FROZEN["z_shift"]) for v in per.values())
    claim = "CONFIRMED" if (c1 >= 2 and c2 and c3 and c4) else "REFUTED" if fail >= 2 * n / 3 else "INCONCLUSIVE"
    r1 = sum(v["R1"] for v in per.values()) >= 2 * n / 3
    r2n = sum(v["R2"] for v in per.values())
    r3 = all(v["R3"] for v in per.values())
    pattern = "HOLDS" if (r1 and r2n >= 2 * n / 3 and r3) else "FAILS" if (n - r2n) >= 2 * n / 3 else "INCONCLUSIVE"
    return dict(claim=claim, pattern=pattern, in_flight_R4_r1b="HOLDS" if blind["R4_r1b"] else "FAILS")


def run_one(folder: Path, seed: int):
    P = hc.load_period(folder)
    out = evaluate(P, seed=seed)
    obs, rb0, rr0 = blind_window(P, seed)
    os.environ["H28_TOUCH"] = "work"
    try:
        Pw = hc.load_period(folder)
        nw = int(hc.build_rows(Pw)[0]["y"].sum())
        out["work"] = evaluate(Pw, seed=seed, work=True) if nw >= FROZEN["min_work_arrivals"] else dict(arrivals=nw, skipped=True)
    finally:
        os.environ.pop("H28_TOUCH", None)
    return out, (obs, rb0, rr0)


def check_builder(dest: Path):
    """Rebuild the stand-ins' ledger exposures with build_r1b_period (non-holdout rows only) and compare."""
    for g, t in TARGETS.items():
        s = t["standin"]
        parts = build_r1b_period(s, OUT, allow_holdout=False)
        write_r1b(parts, dest / "r1b" / gname(s))
        for name in ("exposures", "calls", "touches_work"):
            ref = pl.read_parquet(OUT / "r1b" / gname(s) / f"{name}.parquet")
            same = ref.equals(parts[name])
            print(f"builder check G{s:02d} {name}: rows {parts[name].height} vs r1b {ref.height}; identical={same}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check-builder", type=Path, default=None, help="dry-run only: scratch dir for the builder check")
    ap.add_argument("--dry-out", type=Path, default=OUT / "r1b" / "confirm_r1b_dryrun.json", help="dry-run result file")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    a = ap.parse_args()
    if a.dry_run == a.confirm:
        raise SystemExit("choose exactly one of --dry-run or --confirm")
    per, rows = {}, []
    if a.dry_run:
        ledger_status(strict=False)
        if a.check_builder:
            check_builder(a.check_builder)
        for g, t in TARGETS.items():
            s = t["standin"]
            assert s not in held_goals()
            key = f"standin_{s}_for_{g}"
            per[key], blind = run_one(OUT / gname(s), seed=s)
            rows.append(blind)
            print(s, json.dumps(per[key], default=float), flush=True)
        pb = pool_blind(rows)
        verdict = decide(per, pb)
        a.dry_out.parent.mkdir(parents=True, exist_ok=True)
        a.dry_out.write_text(
            json.dumps(dict(verdict=verdict, blind=pb, per=per, frozen=FROZEN,
                            run_at=dt.datetime.now(dt.timezone.utc).isoformat()), indent=1, default=float))
        print("blind window (pooled stand-ins):", json.dumps(pb, default=float))
        print("DRY RUN verdict on stand-ins:", verdict)
        return
    if not a.ack:
        raise SystemExit("refusing: --confirm needs --i-understand-this-uses-the-locked-holdout")
    must = [Path(__file__).resolve(), HERE / "CONFIRM_R1B.md", HERE.parent / "README.md", HERE / "h28core.py",
            HERE / "r1b_natives.py", HERE.parent / "scheme/build.py", HERE.parent / "scheme/build_r1b.py"]
    if not committed_clean(must):
        raise SystemExit("refusing: commit confirm_r1b.py, CONFIRM_R1B.md, the card, h28core.py, r1b_natives.py and "
                         "scheme/build*.py before the confirmatory run (reuse policy, hypotheses/holdout.md)")
    if not ledger_status(strict=True):
        raise SystemExit("refusing: holdout_ledger.check() reports a same-family prior run on a target; Vivian decides")
    import build as h28build  # noqa: E402
    sh = h28build.Shared()
    out_dir = OUT / "confirm_r1b"
    for g in TARGETS:
        assert g in held_goals(), f"#{g} is not in the holdout"
        h28build.build_period(sh, g, allow_holdout=True, only_holdout=True, out=out_dir)
        write_r1b(build_r1b_period(g, out_dir, allow_holdout=True), out_dir / "r1b" / gname(g))
        per[g], blind = run_one(out_dir / gname(g), seed=g)
        rows.append(blind)
        print(g, json.dumps(per[g], default=float), flush=True)
    pb = pool_blind(rows)
    verdict = decide(per, pb)
    (out_dir / "confirm_r1b_result.json").write_text(json.dumps(dict(verdict=verdict, blind=pb, per=per, frozen=FROZEN),
                                                                indent=1, default=float))
    print("CONFIRMATORY verdict:", verdict)


if __name__ == "__main__":
    main()
