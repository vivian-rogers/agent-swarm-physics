"""Round-2 bookkeeping: per-unit rows to per_period_estimates (round 2 plus a round-1 backfill: H50 had no rows),
a period table (r2/period_table.parquet), and a "Round 2" block in every goal-period README with round-2 numbers.

Usage: uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/r2_write.py [--no-estimates]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import r2lib as R2  # noqa: E402

D = ROOT / "data/processed/H50-field-vs-coupling-transfer-lag"
GP = ROOT / "hypotheses/H50-field-vs-coupling-transfer-lag/goalperiod-subhypotheses"
SRC = "data/processed/H50-field-vs-coupling-transfer-lag/r2"
M_CONT = ("H50 r2 R1: matched-age content read-out jump, hop-1 minus hop-0 (in-flight) statements of the recipient, "
          "10-s age bins over 0-60 s, whitened 32-d cosine to the source minus same-sender placebo (>= 2 h away)")
M_RD = ("H50 r2 R6 (post hoc): start-time RD at the relay posting time on third-party calls, anchors at C-hops >= 2 on "
        "the source's clock, shifted-time placebo, 1-h block bootstrap")
M_K = "H50 r2 R2: K=6 successive-boundary read-out kernel on logged-start recipients (regime I)"
M_R1 = "H50 r1: placebo-corrected read-out jump in P(talk call), first boundary, W = 1.5 x median call interval"


def rows_est():
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet").select("unit_id", "days")
    days = {r["unit_id"]: sorted(r["days"]) for r in pu.iter_rows(named=True)}
    out = []

    def add(unit, g, stat, ch, est, lo, hi, se, n, method, null, post_hoc=False, n_kind="days", src=SRC, notes=None):
        if est is None or not np.isfinite(est):
            return
        ds = days.get(unit, [None])
        out.append(dict(period_unit=unit, goal_no=int(g), statistic=stat, channel=ch, estimate=float(est),
                        ci_lo=None if lo is None or not np.isfinite(lo) else float(lo),
                        ci_hi=None if hi is None or not np.isfinite(hi) else float(hi),
                        se=None if se is None or not np.isfinite(se) else float(se), n=float(n), method=method, null=null,
                        role="replication", ci_level=0.95, ci_kind="percentile", n_kind=n_kind, first_day=ds[0],
                        last_day=ds[-1], post_hoc=post_hoc, source=src, notes=notes))
    c = pl.read_parquet(D / "r2/content_units.parquet").filter(pl.col("eligible") & (pl.col("variant") == "primary"))
    for r in c.iter_rows(named=True):
        add(r["unit"], r["goal_no"], f"content_jump_Jc1_{r['subset']}", f"content_{r['model']}", r["J1"], r["J1_lo"],
            r["J1_hi"], r["J1_se"], r["n_blocks"], M_CONT, "in-flight (hop-0) statements at matched age", n_kind="blocks",
            src=SRC + "/content_units.parquet")
    rd = pl.read_parquet(D / "r2/relay_rd_units.parquet").filter(pl.col("eligible"))
    for r in rd.iter_rows(named=True):
        for lab in ("rd2", "rd2_named", "rd2_unnamed"):
            if r.get(f"{lab}_J") is not None:
                add(r["unit"], r["goal_no"], f"relay_rd_J_{lab}", "talk", r[f"{lab}_J"], r[f"{lab}_lo"], r[f"{lab}_hi"],
                    r[f"{lab}_se"], r["n_triples"], M_RD, "shifted-time placebo", post_hoc=True, n_kind="relay triples",
                    src=SRC + "/relay_rd_units.parquet",
                    notes="valid in regime III only (regime-I RD biased +0.025 in a length-dependent null world)")
    k = pl.read_parquet(D / "r2/kernel_I_units.parquet")
    for r in k.iter_rows(named=True):
        for lab, ch in (("logged", "talk"), ("mode_all", "chat_mode")):
            for h in (1, 4):
                v, se = r.get(f"{lab}_k{h}"), r.get(f"{lab}_k{h}_se")
                if v is not None:
                    add(r["unit"], r["goal_no"], f"kernel_k{h}_{lab}", ch, v, v - 1.96 * se, v + 1.96 * se, se,
                        r.get(f"{lab}_n", 0), M_K, "shifted-time placebo", n_kind="pairs", src=SRC + "/kernel_I_units.parquet")
    ut = pl.read_parquet(D / "unit_table.parquet").filter(~pl.col("ne43"))
    for r in ut.iter_rows(named=True):
        add(r["unit"], r["goal_no"], "readout_jump_J1", "talk", r["J1"], r["J1_lo"], r["J1_hi"], r["J1_se"], r["n_days"],
            M_R1, "shifted-time placebo", src="data/processed/H50-field-vs-coupling-transfer-lag/unit_table.parquet")
        add(r["unit"], r["goal_no"], "activity_field_excess_full", "activity", r["fFex_A_full"], None, None,
            r["fFnullsd_A_full"], r["n_days"], "H50 r1: f_F - f_F,null (measured-input FIR, full window)",
            "shifted-input null", src="data/processed/H50-field-vs-coupling-transfer-lag/unit_table.parquet")
    return out


def period_table():
    c = pl.read_parquet(D / "r2/content_units.parquet").filter(pl.col("eligible") & (pl.col("variant") == "primary") & (pl.col("model") == "bge"))
    rd = pl.read_parquet(D / "r2/relay_rd_units.parquet").filter(pl.col("eligible"))
    k = pl.read_parquet(D / "r2/kernel_I_units.parquet")
    goals = sorted(set(c["goal_no"].to_list()) | set(rd["goal_no"].to_list()) | set(k["goal_no"].to_list()))
    rows = []
    for g in goals:
        r = dict(goal_no=g)
        for sub in ("all", "named", "unnamed"):
            s = c.filter((pl.col("goal_no") == g) & (pl.col("subset") == sub))
            m, se = R2.ivw(s["J1"].to_numpy(), s["J1_se"].to_numpy()) if len(s) else (np.nan, np.nan)
            r[f"Jc1_{sub}"], r[f"Jc1_{sub}_se"], r["n_units_c"] = m, se, len(s) if sub == "all" else r.get("n_units_c")
        s = rd.filter(pl.col("goal_no") == g)
        for lab in ("rd2", "rd2_named"):
            if len(s) and f"{lab}_J" in s.columns:
                ss = s.filter(pl.col(f"{lab}_J").is_not_null())
                r[lab], r[lab + "_se"] = R2.ivw(ss[f"{lab}_J"].to_numpy(), ss[f"{lab}_se"].to_numpy()) if len(ss) else (np.nan, np.nan)
        s = k.filter(pl.col("goal_no") == g)
        for lab in ("logged_k1", "logged_k4", "mode_all_k1"):
            if len(s) and lab in s.columns:
                ss = s.filter(pl.col(lab).is_not_null())
                r[lab], r[lab + "_se"] = R2.ivw(ss[lab].to_numpy(), ss[lab + "_se"].to_numpy()) if len(ss) else (np.nan, np.nan)
        rows.append(r)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(D / "r2/period_table.parquet")
    return df


def fmt(m, se):
    if m is None or se is None or not (np.isfinite(m) and np.isfinite(se)):
        return "–"
    return f"{m:.3f} [{m - 1.96 * se:.3f}, {m + 1.96 * se:.3f}]"


def readmes(pt):
    for r in pt.iter_rows(named=True):
        p = GP / f"G{r['goal_no']:02d}" / "README.md"
        if not p.exists():
            continue
        txt = p.read_text()
        txt = re.sub(r"\n## Round 2 \(2026-10-05\).*?(?=\n## |\Z)", "\n", txt, flags=re.S)
        lines = ["## Round 2 (2026-10-05)",
                 "*Predictions templated from the card's \"Round 2\" section (written 2026-10-05 02:50 UTC, before any round-2 "
                 "statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*",
                 "",
                 "| statistic | estimate [95% CI] | reading |",
                 "| --- | --- | --- |"]
        ca = (r.get("Jc1_all"), r.get("Jc1_all_se"))
        if ca[0] is not None and np.isfinite(ca[0]):
            rd = "content couples at the read-out call" if ca[0] - 1.96 * ca[1] > 0 else "CI includes 0"
            lines.append(f"| R1 content jump J^c_1 (bge, all) | {fmt(*ca)} | {rd} ({r['n_units_c']} unit(s)) |")
            lines.append(f"| R1 J^c_1 named / unnamed | {fmt(r.get('Jc1_named'), r.get('Jc1_named_se'))} / "
                         f"{fmt(r.get('Jc1_unnamed'), r.get('Jc1_unnamed_se'))} | address split |")
        else:
            lines.append("| R1 content jump J^c_1 | – | too few hop-0 / hop-1 rows at 0–60 s (< 200) |")
        if r.get("rd2") is not None and np.isfinite(r.get("rd2") or np.nan):
            note = "post hoc; valid in regime III only" if r["goal_no"] >= 37 else "post hoc; biased in regime I (not scored)"
            lines.append(f"| R6 relay RD, C-hop ≥ 2 (all / naming C) | {fmt(r['rd2'], r['rd2_se'])} / "
                         f"{fmt(r.get('rd2_named'), r.get('rd2_named_se'))} | {note} |")
        if r.get("logged_k1") is not None and np.isfinite(r.get("logged_k1") or np.nan):
            lines.append(f"| R2 kernel, logged-start recipients: k1 / k4 | {fmt(r['logged_k1'], r['logged_k1_se'])} / "
                         f"{fmt(r.get('logged_k4'), r.get('logged_k4_se'))} | regime-I kernel |")
            lines.append(f"| R2 chat-mode channel k1 (all recipients) | {fmt(r.get('mode_all_k1'), r.get('mode_all_k1_se'))} | "
                         "share of calls in chat mode after a read |")
        lines.append("")
        block = "\n".join(lines) + "\n"
        if "\n## Notes" in txt:
            txt = txt.replace("\n## Notes", "\n" + block + "\n## Notes", 1)
        else:
            txt = txt.rstrip() + "\n\n" + block
        p.write_text(txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    pt = period_table()
    readmes(pt)
    print(pt.select("goal_no", "Jc1_all", "rd2", "logged_k1"))
    if not a.no_estimates:
        import estimates as E
        rows = rows_est()
        w = E.write_estimates(rows, hypothesis="H50")
        print("estimates rows written:", w.height)


if __name__ == "__main__":
    main()
