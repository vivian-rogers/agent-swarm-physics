"""H37 scheme, step 1b: which pairs get labelled, and the blind validation sample (codes only).

  selection/g51_sample.parquet   #51 mention/both pairs, <= 40 per unordered agent pair per H22 unit (51a-51e),
                                 random within the cap (seed 20261004)
  validation/sample60.parquet    60 pairs for Claude's blind labels: #12 debate-window 20, #12 other 6, #26 10,
                                 #51 (from the #51 selection) 16, #40 8; random within strata (seed 20261004)

--dump PATH writes the 60 pairs' texts to PATH for blind labelling. PATH must be outside the repository (scratch);
the gated text is never written under the project.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import OUT as SHARED  # noqa: E402

DATA = ROOT / "data/processed/H37-stance-spins"
SEED = 20261004
UNITS51 = {"51a": ("2026-07-06", "2026-07-08"), "51b": ("2026-07-09", "2026-08-04"), "51c": ("2026-08-05", "2026-08-24"),
           "51d": ("2026-08-25", "2026-09-02"), "51e": ("2026-09-03", "2026-09-04")}
CAP51 = 40


def unit_expr():
    e = pl.lit(None, pl.String)
    for u, (a, b) in UNITS51.items():
        e = pl.when((pl.col("pt_date") >= a) & (pl.col("pt_date") <= b)).then(pl.lit(u)).otherwise(e)
    return e


def debate_windows():
    L = json.loads((ROOT / "hypotheses/H21-debate-antiferromagnet/scheme/labels/g12_debates.json").read_text())
    P = dt.datetime.fromisoformat
    ds = [d for d in L["debates"] if d["held"]]
    out = []
    for k, d in enumerate(ds):
        pre = max(P(d["t_lineup"]), P(d["t_motion"]), P(d["t_first_speech"]) - dt.timedelta(minutes=15))
        if k > 0:
            pre = max(pre, out[-1]["post_end"])
        post = P(d["t_verdict"]) + dt.timedelta(minutes=10)
        if k + 1 < len(ds):
            nx = ds[k + 1]
            post = min(post, max(P(nx["t_lineup"]), P(nx["t_motion"]), P(nx["t_first_speech"]) - dt.timedelta(minutes=15)))
        out.append({"debate": d["debate"], "pre_start": pre, "first_speech": P(d["t_first_speech"]), "verdict": P(d["t_verdict"]),
                    "post_end": post, "gov": d["gov"], "opp": d["opp"], "judge": d["judge"], "bench": d["bench"]})
    return out


def g51_selection():
    p = pl.read_parquet(DATA / "pairs/G51.parquet").filter(pl.col("kind") != "adjacent")
    p = p.with_columns(unit_expr().alias("unit"), pl.min_horizontal("agent_a", "agent_b").alias("lo"),
                       pl.max_horizontal("agent_a", "agent_b").alias("hi"))
    assert p["unit"].null_count() == 0
    rng = np.random.default_rng(SEED)
    p = p.with_columns(pl.Series("u", rng.random(p.height)))
    p = p.with_columns(pl.col("u").rank("ordinal").over("unit", "lo", "hi").alias("rk"))
    sel = p.filter(pl.col("rk") <= CAP51).select("pair_id", "unit").sort("pair_id")
    return sel


def validation_sample(sel51):
    rng = np.random.default_rng(SEED + 1)
    parts = []
    p12 = pl.read_parquet(DATA / "pairs/G12.parquet")
    wins = debate_windows()
    indeb = np.zeros(p12.height, bool)
    tb = p12["t_b"].to_list(); ta = p12["t_a"].to_list()
    for w in wins:
        for k in range(p12.height):
            if w["first_speech"] <= tb[k] < w["verdict"] and ta[k] >= w["pre_start"]:
                indeb[k] = True
    p12 = p12.with_columns(pl.Series("indeb", indeb))

    def take(df, n, stratum):
        ix = rng.choice(df.height, n, replace=False)
        return df[np.sort(ix)].select("goal_no", "pair_id").with_columns(pl.lit(stratum).alias("stratum"))
    parts.append(take(p12.filter(pl.col("indeb")), 20, "12-debate"))
    parts.append(take(p12.filter(~pl.col("indeb")), 6, "12-other"))
    parts.append(take(pl.read_parquet(DATA / "pairs/G26.parquet"), 10, "26"))
    parts.append(take(pl.read_parquet(DATA / "pairs/G51.parquet").join(sel51, on="pair_id", how="semi"), 16, "51"))
    parts.append(take(pl.read_parquet(DATA / "pairs/G40.parquet"), 8, "40"))
    s = pl.concat(parts)
    perm = rng.permutation(s.height)  # presentation order shuffled so strata are not visible while labelling
    return s[perm].with_row_index("vid")


def dump(sample, path):
    path = Path(path).resolve()
    assert ROOT not in path.parents, "refusing to write gated text inside the repository"
    names = dict(pl.read_parquet(SHARED / "roster.parquet", columns=["agent", "name"]).iter_rows())
    txt = pl.read_parquet(SHARED / "chat_text.parquet", columns=["message_id", "text"])
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from label_stance import window_around
    lines = []
    for r in sample.iter_rows(named=True):
        p = pl.read_parquet(DATA / f"pairs/G{r['goal_no']:02d}.parquet").filter(pl.col("pair_id") == r["pair_id"]).row(0, named=True)
        ta = txt.filter(pl.col("message_id") == p["msg_a"])["text"][0]
        tb = txt.filter(pl.col("message_id") == p["msg_b"])["text"][0]
        na, nb = names[p["agent_a"]], names[p["agent_b"]]
        lines.append(f"=== V{r['vid']:02d} ===\nA ({na}): {window_around(ta, None, 800)}\nB ({nb}): {window_around(tb, na, 1000)}\n")
    path.write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump")
    a = ap.parse_args()
    (DATA / "selection").mkdir(parents=True, exist_ok=True)
    (DATA / "validation").mkdir(parents=True, exist_ok=True)
    sel = g51_selection()
    sel.write_parquet(DATA / "selection/g51_sample.parquet")
    print("G51 selection", sel.height, sel.group_by("unit").len().sort("unit").to_dicts())
    vpath = DATA / "validation/sample60.parquet"
    if not vpath.exists():
        validation_sample(sel).write_parquet(vpath)
    s = pl.read_parquet(vpath)
    print("validation sample", s.group_by("stratum").len().sort("stratum").to_dicts())
    if a.dump:
        dump(s, a.dump)
        print("dumped texts to scratch")


if __name__ == "__main__":
    main()
