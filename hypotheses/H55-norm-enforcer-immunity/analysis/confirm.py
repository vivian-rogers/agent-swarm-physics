"""H55 confirmatory test on the LOCKED HOLDOUT. Written 2026-10-04 after exploratory round 1; NOT RUN.

Refuses to touch held-out data without:  --confirm --i-understand-this-uses-the-locked-holdout
Dry run (non-holdout stand-ins, identical code path):  --dry-run

Targets (reuse policy: hypotheses/holdout.md; checked with infra/shared/holdout_ledger.py: check()):
  TAIL = #51 tail (2026-09-07 -> 2026-09-21; roles from ground_truth_labels, preferred rows, holdout=True)
  TREP = held-out goal periods G22, G28, G29, G32 (regime I, 9-12 agents)
Stand-ins for --dry-run: TAIL -> #51 head 2026-08-17 -> 2026-09-05; TREP -> G27, G30, G31, G33.

Sensor prerequisite: the Jev correction sensor needs DQ2 `opp_type` on held-out parent "opposes" pairs, which DQ2 did
not label (its subtype pass was non-holdout only). `--label` runs that pass with DQ2's exact question
(infra/shared/reply_threading.py: questions_opp) on held-out parent pairs with stance = opposes, p_reply >= 0.5:
<= 2,380 pairs (DQ2 count incl. holdout), ~$0.000033 each => ~$0.08 (script cap $0.30). Status 2026-10-04: NOT RUN
(shared OpenRouter account out of credit, HTTP 402). C1/C5 need it; C2-C4 do not.

Predictions (frozen 2026-10-04, after exploration, before any holdout statistic). Exploration values in brackets.
  C1 (primary; friction REVERSED): random-effects mean over TREP + TAIL of Spearman rho(c_j, nu_j) < 0, one-sided
     p < 0.05 (Fisher z). [27 periods: -0.24, p 0.04; #51 head -0.60]. Credence 0.5 (5 targets: ~50% power).
  C2 (#51 tail pairs): BH-significant negative pairs (DQ2 hard labels, conf >= 0.8) exceed the calibrated agent-field
     null (p < 0.05), AND the share involving enforcer roles E exceeds the reply-weighted share of E in labelled replies
     (binomial p < 0.10). [head: 16 vs 0.19 expected; E 12/16 vs reply-weighted 0.56, p 0.09]. Credence 0.3.
  C3 (no large immune effect on blocked spells): pooled over TREP + TAIL, the matched agent-demeaned Delta for a
     correction read in a v3 blocked spell has 95% CI upper bound < 0.20. [-0.02, CI -0.12..0.10]. Credence 0.55
     (few treated windows expected; an unscorable result counts as not confirmed).
  C4 (address effect, loops): pooled over TREP, matched Delta for any directed read in a restatement loop > 0,
     p < 0.05. [+0.05, p 1e-4; regime-I driven]. Credence 0.5.
  C5 (HH210 coverage): < 2% of restatement loop episodes in TREP + TAIL receive a Jev correction read.
     [0.65%]. Credence 0.85.
  Decision: confirmed "friction reversed" if C1 passes; "missing immune system" if C3 and C5 pass; else not confirmed.
Output: data/processed/H55-norm-enforcer-immunity/confirm/results.json (or confirm_dryrun.json).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h55lib as L  # noqa: E402
from h55lib import H, NL  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

TAIL = ("2026-09-07", "2026-09-21")
TREP = [22, 28, 29, 32]
STANDIN = {"tail": ("2026-08-17", "2026-09-06"), "trep": [27, 30, 31, 33]}
RNG = np.random.default_rng(20261004)
LABEL_CAP_USD = 0.30


def ledger_checks():
    import holdout_ledger as HL
    out = {}
    for tgt, mod, fam in (("#51-tail", "stance labels", ["stance"]), ("#51-tail", "behavior states", ["behavior_states"]),
                          *[(f"G{g}", "stance labels", ["stance"]) for g in TREP],
                          *[(f"G{g}", "message content", ["dilution_addressing"]) for g in TREP]):
        r = HL.check("H55", tgt, mod, fam)
        out[f"{tgt}|{mod}"] = {"allowed": r["allowed"], "needs_disclosure": r["needs_disclosure"],
                               "prior_runs": [u["hypothesis"] for u in r["prior_runs"]],
                               "competing_planned": sorted({u["hypothesis"] for u in r["competing_planned"]})}
    return out


def build_holdout_tables():
    """Builds OUT/confirm_build/ (messages, loops, blocked, reads) including held-out rows."""
    sch = H.HDIR / "scheme/build.py"
    for step in ("messages", "loops", "blocked", "reads"):
        subprocess.run([sys.executable, str(sch), step, "--allow-holdout"], check=True)
    return H.OUT / "confirm_build"


def label_holdout_opptype(od: Path):
    """Jev opptype pass on held-out parent opposes pairs (behind --label). Not run on 2026-10-04 (HTTP 402)."""
    raise SystemExit("--label: Jev labelling is not run in round 1 (account out of credit). Command when funded:\n"
                     "  uv run --with httpx python hypotheses/H55-norm-enforcer-immunity/analysis/confirm.py --label "
                     "--confirm --i-understand-this-uses-the-locked-holdout   (cap $%.2f; est. ~$0.08)" % LABEL_CAP_USD)


def tail_mask(df, lo, hi, col="pt_date"):
    return df.filter((pl.col("goal_no") == 51) & (pl.col(col) >= lo) & (pl.col(col) < hi))


def run(od: Path, tail: tuple, trep: list, confirm: bool):
    res = {"targets": {"tail": tail, "trep": trep}, "od": str(od), "confirm": confirm}
    msgs = pl.read_parquet(od / "messages.parquet")
    rates_all = L.sender_rates(msgs.filter(pl.col("goal_no").is_in(trep) | ((pl.col("goal_no") == 51) & (pl.col("pt_date") >= tail[0]) & (pl.col("pt_date") < tail[1]))))
    pp = L.pair_table(od, allow_holdout=confirm)
    if not confirm:
        assert not pp["holdout"].any(), "dry run must not see holdout pairs"
    sensor_ok = bool(msgs.filter(pl.col("parent_id").is_not_null() & (pl.col("stance") == "opposes"))["opp_type"].is_not_null().mean() > 0.5) \
        if msgs.filter(pl.col("stance") == "opposes").height else False
    res["sensor_available"] = sensor_ok
    # ---- C1
    rhos, ns, per = [], [], {}
    groups = [(f"G{g}", pp.filter(pl.col("goal_no") == g), rates_all.filter(pl.col("goal_no") == g)) for g in trep]
    tp = tail_mask(pp, *tail)
    tm = tail_mask(msgs, *tail)
    groups.append(("tail", tp, L.sender_rates(tm).filter(pl.col("goal_no") == 51)))
    for nm, p, rt in groups:
        fa = L.friction_agent(p, rt, R=5000, rng=RNG) if sensor_ok else {"scorable": False, "why": "sensor unavailable"}
        per[nm] = {k: fa.get(k) for k in ("scorable", "rho", "p", "rho_partial", "n_agents", "why")}
        if fa.get("scorable"):
            rhos.append(fa["rho"]); ns.append(fa["n_agents"])
    meta = L.fisher_z_meta(rhos, ns) if rhos else {"k": 0}
    p_one = float(stats.norm.cdf(meta["z"])) if meta.get("k") else None
    res["C1"] = {"per_target": per, "meta": meta, "p_one_less": p_one, "pass": bool(p_one is not None and p_one < 0.05)}
    # ---- C2 (#51 tail pairs)
    roles = pl.read_parquet(H.SH / "ground_truth_labels.parquet").filter((pl.col("goal_no") == 51) & pl.col("preferred") & (pl.col("label_kind") == "role"))
    roles = roles.filter(pl.col("holdout") == confirm) if confirm else roles.filter(~pl.col("holdout"))
    E = set(roles.filter(pl.col("value").is_in(list(H.ENFORCER_ROLES)))["agent"].to_list())
    if tp.height >= 200:
        agl, a_f, b_f, ok, spk, tgt = L.fit_fields(tp)
        y = tp["y"].to_numpy().astype(float)
        N = len(agl)
        isE = np.array([a in E for a in agl])

        def sig(yy):
            J, C, r, key = NL._residual_matrix(spk, tgt, yy, N, 3)
            pv, kk = [], []
            for k_ in np.unique(key):
                rr = r[key == k_]
                if len(rr) >= 3 and rr.std(ddof=1) > 0:
                    pv.append(stats.t.cdf(rr.mean() / (rr.std(ddof=1) / np.sqrt(len(rr))), len(rr) - 1)); kk.append(k_)
            pv, kk = np.array(pv), np.array(kk)
            if not len(pv):
                return 0, 0
            o = np.argsort(pv)
            okk = pv[o] <= 0.1 * np.arange(1, len(pv) + 1) / len(pv)
            ns_ = int(np.flatnonzero(okk).max() + 1) if okk.any() else 0
            s_ = kk[o][:ns_]
            return ns_, int(np.sum(isE[s_ // N] | isE[s_ % N]))
        nsig, nE = sig(y)
        null = [sig(ys) for ys in NL.agent_field_null(spk, tgt, y, N, 200, RNG)]
        ns0 = np.array([x[0] for x in null])
        wE = float((tp["a_agent"].is_in(list(E)) | tp["b_agent"].is_in(list(E))).mean())
        pbin = float(stats.binomtest(nE, nsig, wE, alternative="greater").pvalue) if nsig else 1.0
        psig = float((1 + np.sum(ns0 >= nsig)) / 201)
        res["C2"] = {"n_sig": nsig, "n_E": nE, "null_mean": float(ns0.mean()), "p_sig": psig, "reply_weighted_E": wE,
                     "p_binom": pbin, "pass": bool(psig < 0.05 and pbin < 0.10), "E": sorted(E)}
    else:
        res["C2"] = {"pass": False, "why": f"tail pairs {tp.height} < 200"}
    # ---- C3/C4/C5: steps
    def steps(kind):
        if kind == "loop":
            st = pl.read_parquet(od / "loop_steps.parquet").filter((pl.col("version") == "restate") & pl.col("y").is_not_null())
            rd = pl.read_parquet(od / "reads_loop.parquet")
            s = L.steps_with_reads(st, rd, pl.read_parquet(od / "reads_loop_volume.parquet"), "anchor_id")
        else:
            st = pl.read_parquet(od / "blocked_steps.parquet").filter(pl.col("y").is_not_null())
            st = st.with_columns((pl.col("t0").cast(pl.Int64).cast(pl.Utf8) + "_" + pl.col("agent").cast(pl.Utf8)).alias("win_id"))
            rd = pl.read_parquet(od / "reads_blocked.parquet").with_columns(pl.lit(None, pl.Float32).alias("novelty"))
            s = L.steps_with_reads(st, rd, pl.read_parquet(od / "reads_blocked_volume.parquet"), "win_id")
        inT = pl.col("goal_no").is_in(trep) | ((pl.col("goal_no") == 51) & (pl.col("pt_date") >= tail[0]) & (pl.col("pt_date") < tail[1]))
        return s.filter(inT)
    sb = steps("blocked")
    c3 = L.immune_contrast(sb, rng=RNG, B=2000, min_treated=10) if sensor_ok else {"scorable": False, "why": "sensor unavailable"}
    c3.pop("diffs", None); c3.pop("clusters", None)
    c3["pass"] = bool(c3.get("scorable") and c3["hi"] < 0.20)
    res["C3"] = c3
    sl = steps("loop")
    c4 = L.address_contrast(sl.filter(pl.col("goal_no").is_in(trep)), rng=RNG, B=2000)
    c4["pass"] = bool(c4.get("scorable") and c4["delta"] > 0 and c4["p"] < 0.05)
    res["C4"] = c4
    if sensor_ok:
        rd = pl.read_parquet(od / "reads_loop.parquet").group_by("anchor_id").agg(pl.col("corr_jev").sum().alias("nc"))
        e = sl.join(rd, left_on="message_id", right_on="anchor_id", how="left").group_by("episode").agg(pl.col("nc").fill_null(0).sum())
        share = float((e["nc"] > 0).mean()) if e.height else None
        res["C5"] = {"episodes": e.height, "share": share, "pass": bool(share is not None and share < 0.02)}
    else:
        res["C5"] = {"pass": False, "why": "sensor unavailable"}
    res["decision"] = {"friction_reversed_confirmed": res["C1"]["pass"], "missing_immune_confirmed": res["C3"]["pass"] and res["C5"]["pass"]}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="iu", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--label", action="store_true")
    a = ap.parse_args()
    out = H.OUT / "confirm"
    out.mkdir(exist_ok=True)
    if a.dry_run:
        res = run(H.OUT, STANDIN["tail"], STANDIN["trep"], confirm=False)
        res["ledger"] = ledger_checks()
        res["ran_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        (out / "confirm_dryrun.json").write_text(json.dumps(res, indent=1, default=str))
        print(json.dumps({k: (v if k in ("decision", "sensor_available") else {kk: vv for kk, vv in v.items() if kk in ("pass", "meta", "delta", "hi", "share", "n_sig", "p_sig", "p_binom", "why")} if isinstance(v, dict) else v) for k, v in res.items() if k != "ledger"}, indent=1, default=str))
        return
    if not (a.confirm and a.iu):
        raise SystemExit("refusing: this script uses the locked holdout. Pass --confirm --i-understand-this-uses-the-locked-holdout "
                         "(after the predictions in the docstring are committed and the ledger disclosure is done), or --dry-run.")
    chk = ledger_checks()
    blocked = [k for k, v in chk.items() if not v["allowed"]]
    if blocked:
        raise SystemExit(f"holdout ledger: same-family prior run on {blocked}; see hypotheses/holdout.md reuse policy")
    od = build_holdout_tables()
    if a.label:
        label_holdout_opptype(od)
    res = run(od, TAIL, TREP, confirm=True)
    res["ledger"] = chk
    res["ran_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    (out / "results.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res["decision"], indent=1))


if __name__ == "__main__":
    main()
