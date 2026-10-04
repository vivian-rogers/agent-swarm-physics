"""H131 confirmatory run on the LOCKED HOLDOUT. Written and frozen 2026-10-04 after round 1; NOT RUN.

Guard: the held-out path needs BOTH `--confirm` and H131_CONFIRM=1, a matching frozen SHA-256 (`confirm.sha256`), and
`holdout_ledger.check` allowing every target; it writes only under data/processed/H131-antagonism-off-one-readout/confirm/.
`--dry-run` runs the identical code on non-holdout stand-ins (#12 standing in for a held-out debate-style settlement,
#26 for an election-style settlement) and never reads held-out rows.

Targets: every held-out goal period whose preferred DQ6 rows date a settlement with a chat message
(label_kind 'debate_result', or 'phase' with value 'result') and name rivals ('team' rows with opposite sides, or the
runoff candidates of a 'tally' row with label 'runoff'). Candidates scanned: #29, #34, #45-#50, #1, #14, #15, #28, #43.
A target without such rows is reported 'untestable' (no settlement message to read).
Held-out stance: data/processed/holdout_labels/reply_stance_v2_holdout.parquet (prepared by DQ10, never inspected);
flag = stance2 == 'disagree' and stance2_conf >= 0.6 and a_kind == 0 (agent parent), as `disagree_validated_agent`.

Frozen predictions (per target with a settlement):
  C0 (precondition for the HH's kill test): >= 10 in-flight rival replies (posted after the settlement message, produced
     by a call assembled before the speaker's ledger read of it). If < 10: C1 untestable.
  C1 (kill test, HH374): in-flight rival replies keep the open rate: their flag rate exceeds the read rival replies'
     after the settlement (one-sided Fisher exact p < 0.05). Clock alignment (the kill) = in-flight rate within the 90%
     CI of the read rate. Credence 0.4 conditional on C0.
  C2 (replication of round 1): read-gated settlement DiD Delta > 0 with relation-permutation p < 0.05, where >= 20 open
     rival replies exist. Credence 0.5.
Usage:
  uv run python hypotheses/H131-antagonism-off-one-readout/analysis/confirm.py --dry-run
  H131_CONFIRM=1 uv run python hypotheses/H131-antagonism-off-one-readout/analysis/confirm.py --confirm
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import fisher_exact

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h131lib as L  # noqa: E402

ROOT = HERE.parents[2]
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(ROOT / "infra/shared"))
import visibility as V  # noqa: E402

OUT = ROOT / "data/processed/H131-antagonism-off-one-readout/confirm"
SCRATCH = Path(os.environ.get("TMPDIR", "/tmp")) / "h131_confirm_dry"
CANDIDATES = [29, 34, 45, 46, 47, 48, 49, 50, 1, 14, 15, 28, 43]
STANDINS = [12, 26]
FROZEN = dict(min_inflight=10, min_open_rival=20, B_perm=5000, conf=0.6)


def settlements(gt: pl.DataFrame, g: int):
    """List of (unit, settlement message id, t, sides dict agent -> side, rule) from DQ6 rows of goal g."""
    out = []
    x = gt.filter(pl.col("goal_no") == g)
    for r in x.filter(pl.col("label_kind") == "debate_result").iter_rows(named=True):
        team = x.filter((pl.col("label_kind") == "team") & (pl.col("unit") == r["unit"]))
        sides = {int(a): v for a, v in zip(team["agent"], team["value"]) if v in ("gov", "opp")}
        if r["source_ref"] and len(set(sides.values())) == 2:
            out.append((r["unit"], r["source_ref"].split("=")[-1], r["t_valid_from"], sides, "teams",
                        team["t_valid_from"].min(), team["t_valid_to"].max()))
    res = x.filter((pl.col("label_kind") == "phase") & (pl.col("value") == "result"))
    tal = x.filter((pl.col("label_kind") == "tally") & (pl.col("unit") == "runoff"))
    if res.height and tal.height:
        r = res.sort("t_valid_from").row(0, named=True)
        sides = {int(a): "rival" for a in tal["agent"].to_list()}
        out.append(("runoff", r["source_ref"].split("=")[-1], r["t_valid_from"], sides, "runoff", None, None))
    return out


def replies_for(g, settle, stance, pc, tc_holdout):
    unit, m_id, t_v, sides, rule, t0, t1 = settle
    rc = V.receipts([m_id])
    rv = {int(a): t for a, t in zip(rc["recipient"], rc["t_call"])}
    d = stance.filter(pl.col("goal_no") == g).join(pc, on="B_message_id", how="left")
    if rule == "teams":
        d = d.filter((pl.col("tB") >= t0) & (pl.col("tB") < t1) & pl.col("j").is_in(list(sides))
                     & pl.col("i").is_in(list(sides)))
        R = [int(sides[int(a)] != sides[int(b)]) for a, b in zip(d["j"], d["i"])]
    else:
        day = t_v.date()
        d = d.filter((pl.col("tB").dt.date() >= day) & (pl.col("tB") < t_v + pl.duration(days=4)))
        R = [int(int(a) in sides and int(b) in sides) for a, b in zip(d["j"], d["i"])]
    d = d.with_columns(pl.Series("R", R, dtype=pl.Int8), pl.lit(t_v).alias("t_verdict"),
                       pl.col("j").replace_strict(rv, default=None, return_dtype=pl.Datetime("us", "UTC")).alias("t_read"))
    d = d.with_columns((pl.col("tB") >= pl.col("t_verdict")).alias("clock"),
                       (pl.col("t_read").is_not_null() & (pl.col("t_call_prod") >= pl.col("t_read"))).alias("read"))
    return d.with_columns((pl.col("clock") & ~pl.col("read")).alias("inflight"), pl.lit(unit).alias("unit"))


def test_target(df: pl.DataFrame) -> dict:
    riv = df.filter(pl.col("R") == 1)
    infl = riv.filter(pl.col("inflight"))
    rd = riv.filter(pl.col("clock") & pl.col("read"))
    op = riv.filter(~pl.col("clock"))
    out = dict(n=df.height, n_inflight_rival=infl.height, n_read_rival=rd.height, n_open_rival=op.height)
    if infl.height >= FROZEN["min_inflight"] and rd.height:
        a, b = int(infl["y"].sum()), int(rd["y"].sum())
        _, p = fisher_exact([[a, infl.height - a], [b, rd.height - b]], alternative="greater")
        rr = rd["y"].to_numpy().astype(float)
        boots = [np.random.default_rng(k).choice(rr, len(rr)).mean() for k in range(2000)]
        lo, hi = np.percentile(boots, [5, 95])
        r_in = a / infl.height
        out.update(C1="pass" if p < 0.05 else ("kill" if lo <= r_in <= hi else "inconclusive"), C1_p=p,
                   rate_inflight=r_in, rate_read=b / rd.height)
    else:
        out["C1"] = "untestable"
    if op.height >= FROZEN["min_open_rival"]:
        x = df.with_columns(pl.when(pl.col("clock") & pl.col("read")).then(pl.lit("post")).otherwise(pl.lit("deb"))
                            .alias("phase"), pl.lit("C").alias("period"))
        y = x["y"].to_numpy().astype(float)
        Rv = x["R"].to_numpy()
        O = (x["phase"] == "deb").to_numpy().astype(int)
        j, i = x["j"].to_numpy(), x["i"].to_numpy()
        cell = np.array([hash((u, p)) % 10 ** 6 for u, p in zip(x["unit"], x["phase"])])
        dlt = L.did(y, Rv, O, j, i, cell)[0]
        rng = np.random.default_rng(131)
        null = []
        for _ in range(FROZEN["B_perm"]):
            # permutation of the relation labels within unit (keeps the count of rival replies per unit)
            Rp = Rv.copy()
            for u in np.unique(x["unit"].to_numpy()):
                s = np.flatnonzero(x["unit"].to_numpy() == u)
                Rp[s] = rng.permutation(Rp[s])
            null.append(L.did(y, Rp, O, j, i, cell)[0])
        p = float((np.sum(np.array(null) >= dlt) + 1) / (len(null) + 1))
        out.update(C2="pass" if (dlt > 0 and p < 0.05) else "fail", C2_delta=dlt, C2_p=p)
    else:
        out["C2"] = "untestable"
    return out


def run(goals, allow_holdout):
    gt = pl.read_parquet(SH / "ground_truth_labels.parquet").filter(pl.col("preferred"))
    gt = gt.filter(pl.col("holdout") if allow_holdout else ~pl.col("holdout"))
    pc = pl.read_parquet(SH / "producing_calls.parquet").select(pl.col("message_id").alias("B_message_id"),
                                                                pl.col("t").alias("tB"), "t_call_prod")
    if allow_holdout:
        hs = pl.read_parquet(ROOT / "data/processed/holdout_labels/reply_stance_v2_holdout.parquet")
        stance = hs.filter(pl.col("a_kind") == 0).with_columns(
            ((pl.col("stance2") == "disagree") & (pl.col("stance2_conf") >= FROZEN["conf"])).cast(pl.Int8).alias("y"))
    else:
        stance = pl.read_parquet(SH / "reply_stance_v2.parquet").filter(pl.col("labelled") & (pl.col("a_kind") == 0)
                                                                        & ~pl.col("holdout"))
        stance = stance.with_columns(pl.col("disagree_validated_agent").cast(pl.Int8).alias("y"))
    stance = stance.select("B_message_id", "goal_no", pl.col("b_agent").alias("j"), pl.col("a_agent").alias("i"), "y")
    res = {}
    for g in goals:
        st = settlements(gt, g)
        if not st:
            res[f"G{g}"] = dict(status="untestable", reason="no DQ6 settlement message with named rivals")
            continue
        df = pl.concat([replies_for(g, s, stance, pc, None) for s in st], how="diagonal_relaxed")
        res[f"G{g}"] = dict(status="tested", n_settlements=len(st), **test_target(df))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if a.dry_run:
        SCRATCH.mkdir(parents=True, exist_ok=True)
        res = run(STANDINS, allow_holdout=False)
        (SCRATCH / "confirm_dryrun.json").write_text(json.dumps(dict(sha256=sha, dry_run=True, **res), indent=1,
                                                                default=str))
        print(json.dumps(res, indent=1, default=str))
        return
    if not (a.confirm and os.environ.get("H131_CONFIRM") == "1"):
        sys.exit("refusing: confirmatory run needs --confirm and H131_CONFIRM=1 (Vivian's sign-off)")
    shaf = HERE / "confirm.sha256"
    if not shaf.exists() or shaf.read_text().strip() != sha:
        sys.exit("refusing: confirm.py differs from its frozen SHA-256 (confirm.sha256)")
    import holdout_ledger as HL
    for g in CANDIDATES:
        chk = HL.check("H131", f"G{g}", "stance", ["stance"])
        if not chk["allowed"]:
            sys.exit(f"refusing: holdout ledger blocks G{g}: {chk['prior_runs_same_family']}")
    OUT.mkdir(parents=True, exist_ok=True)
    res = run(CANDIDATES, allow_holdout=True)
    (OUT / "confirm_result.json").write_text(json.dumps(dict(sha256=sha, dry_run=False, **res), indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
