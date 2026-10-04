"""Shared per-period estimates table (DQ8): one long table every hypothesis can write, so periods can be compared as
points on a phase diagram (H51 "one dial") and replications are not confused with independent tests.

Table: data/processed/shared/per_period_estimates.parquet. Schema and rules: infra/data-quality/estimates_schema.md.
  required  hypothesis, period_unit, goal_no, statistic, channel, estimate, ci_lo, ci_hi, n, method, null, role,
            holdout, regime, built_at, git_commit
  optional  ci_level, ci_kind, se, n_kind, unit_local, first_day, last_day, confirmatory, post_hoc, status, source,
            source_mtime, notes

Writer (for hypothesis pipelines):
    import estimates as E
    E.write_estimates(rows, hypothesis="H25")      # rows: list of dicts or a polars frame with the columns above
  - fills built_at, git_commit; derives holdout and regime from goal_no / period_unit (hypotheses/holdout.json,
    period_units); refuses held-out rows unless confirmatory=True (the holdout ledger then has to list the run);
  - replaces the hypothesis's earlier rows with the same (statistic, channel, method, role, source) and appends.
  ci_from_se(est, se, level, df=None) gives z or t intervals for sources that store only an SE.
  read_estimates(**filters) returns the table (optionally filtered by column equality).

Backfill (read-only on hypothesis outputs): uv run python infra/shared/estimates.py --backfill
  Extracts the cheap, unambiguous per-period statistics listed in BACKFILL (DQ8 survey, 2026-10-04) and writes them
  with role from the spec and source = the file they came from. Coverage is printed and documented.
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import datetime as dt  # noqa: E402
import glob  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import OUT, ROOT, git_commit, load_holdout  # noqa: E402

PATH = OUT / "per_period_estimates.parquet"
PROC = ROOT / "data/processed"

SCHEMA = {
    "hypothesis": pl.String, "period_unit": pl.String, "goal_no": pl.Int16, "statistic": pl.String,
    "channel": pl.String, "estimate": pl.Float64, "ci_lo": pl.Float64, "ci_hi": pl.Float64, "n": pl.Float64,
    "method": pl.String, "null": pl.String, "role": pl.String, "holdout": pl.Boolean, "regime": pl.String,
    "built_at": pl.Datetime("us", "UTC"), "git_commit": pl.String,
    # optional
    "ci_level": pl.Float64, "ci_kind": pl.String, "se": pl.Float64, "n_kind": pl.String, "unit_local": pl.String,
    "first_day": pl.String, "last_day": pl.String, "confirmatory": pl.Boolean, "post_hoc": pl.Boolean,
    "status": pl.String, "source": pl.String, "source_mtime": pl.String, "notes": pl.String,
}
REQUIRED = list(SCHEMA)[:16]
ROLES = {"replication", "native"}
CI_KINDS = {"percentile", "se_z", "se_t", "profile", "jackknife_z", "parametric", "none"}


# ============================================================================================ helpers
def ci_from_se(est, se, level: float = 0.95, df: float | None = None):
    """(lo, hi) = est -/+ q * se with q from the normal (df None) or t(df) distribution."""
    from scipy.stats import norm, t
    if est is None or se is None or not (math.isfinite(est) and math.isfinite(se)):
        return (None, None)
    q = norm.ppf(0.5 + level / 2) if df is None else t.ppf(0.5 + level / 2, max(df, 1))
    return (est - q * se, est + q * se)


_PU = None


def period_units() -> pl.DataFrame:
    global _PU
    if _PU is None:
        _PU = pl.read_parquet(OUT / "period_units.parquet")
    return _PU


def regime_of(goal_no: int | None) -> str | None:
    if goal_no is None:
        return None
    r = sorted(set(period_units().filter(pl.col("goal_no") == goal_no)["regime"].to_list()))
    return "/".join(r) if r else None


def unit_days(period_unit: str) -> list[str] | None:
    pu = period_units().filter(pl.col("unit_id") == period_unit)
    return sorted(pu["days"][0]) if pu.height else None


def map_unit(goal_no: int, first_day: str | None = None, last_day: str | None = None) -> str:
    """Shared unit id whose days span exactly [first_day, last_day]; 'G<NN>' for a whole goal period (no dates, or
    dates covering all its units); else '' (caller keeps a local id)."""
    pu = period_units().filter(pl.col("goal_no") == goal_no).sort("seq")
    if first_day is None:
        return pu["unit_id"][0] if pu.height == 1 else f"G{goal_no:02d}"
    hit = pu.filter((pl.col("first_day") == first_day) & (pl.col("last_day") == last_day))
    if hit.height == 1:
        return hit["unit_id"][0]
    if pu.height and first_day <= pu["first_day"].min() and last_day >= pu["last_day"].max():
        return pu["unit_id"][0] if pu.height == 1 else f"G{goal_no:02d}"
    return ""


def holdout_of(goal_no: int | None, period_unit: str | None, first_day: str | None = None,
               last_day: str | None = None) -> bool:
    h = load_holdout()
    if goal_no is not None and goal_no in set(h["goal_periods_held_out"]):
        return True
    days = None
    if period_unit and not period_unit.startswith(("G", "local:")):
        days = unit_days(period_unit)
    elif first_day and last_day:
        cal = pl.read_parquet(OUT / "calendar.parquet")
        days = cal.filter(pl.col("pt_date").is_between(first_day, last_day))["pt_date"].to_list()
    elif goal_no is not None:
        days = sorted(d for ds in period_units().filter(pl.col("goal_no") == goal_no)["days"].to_list() for d in ds)
        # a whole goal period counts as held out only if all of it is (e.g. #51 is not; its tail is a window)
        wins = [(w["start"], w["end"]) for w in h["ne_windows"]]
        return bool(days) and all(any(s <= d < e for s, e in wins) for d in days)
    if not days:
        return False
    wins = [(w["start"], w["end"]) for w in h["ne_windows"]]
    return any(any(s <= d < e for s, e in wins) for d in days)


def _frame(rows) -> pl.DataFrame:
    if isinstance(rows, pl.DataFrame):
        df = rows
    else:
        df = pl.DataFrame(rows, infer_schema_length=None) if rows else pl.DataFrame()
    for c, t in SCHEMA.items():
        if c not in df.columns:
            df = df.with_columns(pl.lit(None, dtype=t).alias(c))
    return df.select([pl.col(c).cast(t, strict=False) for c, t in SCHEMA.items()])


def validate(df: pl.DataFrame) -> list[str]:
    errs = []
    for c in ("hypothesis", "period_unit", "statistic", "method", "role"):
        if df[c].null_count():
            errs.append(f"{c}: {df[c].null_count()} nulls")
    bad = set(df["role"].drop_nulls().unique().to_list()) - ROLES
    if bad:
        errs.append(f"role not in {ROLES}: {bad}")
    badk = set(df["ci_kind"].drop_nulls().unique().to_list()) - CI_KINDS
    if badk:
        errs.append(f"ci_kind not in {CI_KINDS}: {badk}")
    inv = df.filter(pl.col("ci_lo").is_not_null() & pl.col("ci_hi").is_not_null() & (pl.col("ci_lo") > pl.col("ci_hi")))
    if inv.height:
        errs.append(f"{inv.height} rows with ci_lo > ci_hi")
    held = df.filter(pl.col("holdout") & ~pl.col("confirmatory").fill_null(False))
    if held.height:
        errs.append(f"{held.height} held-out rows without confirmatory=True: "
                    f"{held.select('hypothesis', 'period_unit').unique().rows()[:5]}")
    return errs


def complete(df: pl.DataFrame) -> pl.DataFrame:
    """Fill built_at, git_commit, regime, holdout where missing."""
    now = dt.datetime.now(dt.timezone.utc)
    gc = git_commit()
    rows = df.to_dicts()
    for r in rows:
        r["built_at"] = r["built_at"] or now
        r["git_commit"] = r["git_commit"] or gc
        if r["regime"] is None:
            r["regime"] = regime_of(r["goal_no"])
        if r["holdout"] is None:
            r["holdout"] = holdout_of(r["goal_no"], r["period_unit"], r.get("first_day"), r.get("last_day"))
        if r["confirmatory"] is None:
            r["confirmatory"] = False
    return _frame(rows)


def read_estimates(path: Path = PATH, **filters) -> pl.DataFrame:
    if not Path(path).exists():
        return _frame([])
    df = pl.read_parquet(path)
    for k, v in filters.items():
        df = df.filter(pl.col(k).is_in(v) if isinstance(v, (list, tuple, set)) else (pl.col(k) == v))
    return df


def write_estimates(rows, hypothesis: str, path: Path = PATH, replace_keys=("statistic", "channel", "method", "role",
                                                                              "source")) -> pl.DataFrame:
    """Validate and upsert one hypothesis's rows (see module docstring). Returns the rows written."""
    df = _frame(rows).with_columns(pl.lit(hypothesis).alias("hypothesis"))
    df = complete(df)
    errs = validate(df)
    if errs:
        raise ValueError("estimates rejected: " + "; ".join(errs))
    old = read_estimates(path)
    if old.height:
        keys = df.select(list(replace_keys)).unique()
        drop = old.filter(pl.col("hypothesis") == hypothesis).join(keys, on=list(replace_keys), how="semi", nulls_equal=True)
        old = old.join(drop, on=list(SCHEMA), how="anti", nulls_equal=True)
    out = pl.concat([old, df]).sort("hypothesis", "statistic", "goal_no", "period_unit")
    out.write_parquet(path, compression="zstd")
    return df


# ============================================================================================ backfill
def _get(obj, path: str):
    """Dotted path with [i] indices, e.g. 'primary.addr.D[0]' or 'b1.delta_ci95[1]'. None when missing."""
    cur = obj
    for tok in re.findall(r"[^.\[\]]+|\[\d+\]", path):
        if cur is None:
            return None
        if tok.startswith("["):
            i = int(tok[1:-1])
            cur = cur[i] if isinstance(cur, (list, tuple)) and len(cur) > i else None
        else:
            cur = cur.get(tok) if isinstance(cur, dict) else None
    return cur


def _num(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


GOAL_RX = re.compile(r"/G(\d{2})([a-z]?)/")


# A spec: h, src (glob relative to data/processed), fmt (parquet | json | json_rows | json_list), plus
#   rows: json path to a list of row dicts (json_rows) ; filter: callable(row) -> bool
#   goal: column / key with the goal number, or "folder" (G<NN> in the path) ; unit: column / key / "folder" / None
#   expand: (json path to a dict, name) -> one row per key, '{k}' in stat paths (e.g. H01 per-unit, H39 levers)
#   stats: list of dicts: statistic, est, lo, hi (paths), se (path), level, ci_kind, df (path or number), n, n_kind,
#          channel (constant or {k}), method, null, role (default replication), post_hoc, status, notes
B = []


def spec(**kw):
    B.append(kw)


spec(h="H03", src="H03-self-excited-criticality/period_table.parquet", fmt="parquet", goal="goal_no",
     filter=lambda r: r["set"] in ("TALK", "ALL"),
     stats=[dict(statistic="hawkes_branching_n", channel="{set}", est="n", lo="n_boot_lo", hi="n_boot_hi", level=0.95,
                 ci_kind="percentile", n="n_events", n_kind="events",
                 method="pooled univariate Hawkes M1_B2 (exp kernel, B2 baseline + exogenous kernels); day bootstrap",
                 null=None)])
spec(h="H05", src="H05-rooms-cut/mf_blocks.json", fmt="json", expand=("MF1.talk", "g"), goal="{k}",
     stats=[dict(statistic="mf_block_J_in_minus_out", channel="talk", est="MF1.talk.{k}.J_in_minus_out",
                 lo="MF1.talk.{k}.J_in_minus_out_ci95[0]", hi="MF1.talk.{k}.J_in_minus_out_ci95[1]", level=0.95,
                 ci_kind="percentile", n="MF1.talk.{k}.days", n_kind="days",
                 method="two-block naive mean-field inversion of excess equal-time correlations; day bootstrap",
                 null="room-label permutation")])
spec(h="H08", src="H08-context-is-the-coupling/G*/c9.json", fmt="json", goal="folder",
     stats=[dict(statistic="readout_gate_jump_D", channel=ch, est=f"primary.{ch}.D[0]", lo=f"primary.{ch}.D[1]",
                 hi=f"primary.{ch}.D[2]", level=0.95, ci_kind="percentile", n="primary.n_real", n_kind="messages",
                 method="D = G(1) - G(0) read-out gate jump vs pseudo messages; day-cluster bootstrap",
                 null="pseudo-message baseline") for ch in ("addr", "talk")])
spec(h="H10", src="H10-goals-are-legendre-pushes/G*/period*.json", fmt="json", goal="folder",
     stats=[dict(statistic="loop_gain_g_along_goal",
                 channel=lambda r, k: "content" + (f" (along {r['_file_suffix']})" if r.get("_file_suffix") else ""),
                 est="g", lo="g_ci90[0]", hi="g_ci90[1]",
                 level=0.90, ci_kind="percentile", n="n_agents", n_kind="agents",
                 method="noise-corrected swarm/independent variance ratio along the goal direction; day bootstrap",
                 null=None, notes="free periods measured along the next goal's direction")])
spec(h="H11", src="H11-potts-labor-vs-herding/results_round1.parquet", fmt="parquet", goal="goal",
     filter=lambda r: bool(r["tested"]),
     stats=[dict(statistic="potts_coupling_bJ_CW", channel="project", est="bj_cw", se="se_cw", df="n_days-1",
                 level=0.95, ci_kind="se_t", n="n_days", n_kind="days",
                 method="Curie-Weiss Potts coupling MLE with day fields; leave-one-day-out jackknife SE",
                 null="N1 label permutation", notes="labels change ~8% under shared project_states")])
spec(h="H12", src="H12-groupthink-dimensional-collapse/unit_table.parquet", fmt="parquet", goal="goal_no", unit="unit",
     filter=lambda r: bool(r["scored"]),
     stats=[dict(statistic="lambda1_over_crossday_edge", channel="activity", est="l1_edge", n="N_act", n_kind="agents",
                 ci_kind="none", method="largest correlation eigenvalue / cross-day surrogate 95% edge (1-min spins)",
                 null="cross-day surrogate"),
            dict(statistic="collective_mode_count_k_cd", channel="activity", est="k_cd", n="N_act", n_kind="agents",
                 ci_kind="none", method="eigenvalues above the cross-day surrogate edge", null="cross-day surrogate")])
spec(h="H13", src="H13-family-fields/G*/results_u*.json", fmt="json", goal="folder", unit="file_u",
     filter=lambda r: r.get("counted", True) is not False,
     stats=[dict(statistic="family_field_T", channel="content", est="a1.obs", se="a1.se_jack", level=0.95,
                 ci_kind="jackknife_z", n="N", n_kind="agents",
                 method="within- minus across-family cosine of agent mean vectors; leave-one-agent-out jackknife",
                 null="lab-label permutation"),
            dict(statistic="family_coupling_delta", channel="talk", est="b1.delta", lo="b1.delta_ci95[0]",
                 hi="b1.delta_ci95[1]", level=0.95, ci_kind="percentile", n="b1.n_agents", n_kind="agents",
                 method="J_in - J_out from family mean-field inversion of pair-day excess correlations; day bootstrap",
                 null="lab permutation")])
spec(h="H14", src="H14-behavior-entropy-production/G*/results.json", fmt="json", goal="folder",
     stats=[dict(statistic="frac_agents_ep_above_null", channel="behavior", est="P2_frac_above_null_newton",
                 n="P2_n", n_kind="agents", ci_kind="none",
                 method="share of agents with single-agent EP (cross-fitted Newton) above a detailed-balance null",
                 null="detailed-balance surrogate"),
            dict(statistic="collective_ep_excess_mf", channel="activity", est="collective.delta_mf_exc",
                 n="collective.N", n_kind="agents", ci_kind="none",
                 method="mean-field collective EP minus cross-day surrogate mean", null="cross-day surrogate")])
spec(h="H15", src="H15-semantic-information-scrambles/G*/result.json", fmt="json", goal="folder",
     filter=lambda r: isinstance(r.get("CTX"), dict),
     stats=[dict(statistic="context_erasure_write_dip", channel="writes", est="CTX.posthoc_rd.CF.rel_dip",
                 lo="CTX.posthoc_rd.CF.lo", hi="CTX.posthoc_rd.CF.hi", level=0.95, ci_kind="percentile",
                 n="CTX.posthoc_rd.CF.n", n_kind="events", post_hoc=True,
                 method="writes in turns +1..+10 over -20..-11 around forced consolidations, minus 1; agent-day bootstrap",
                 null=None)])
spec(h="H16", src="H16-metastable-traps-kramers/summary.json", fmt="json_rows", rows="rows", goal="period",
     stats=[dict(statistic="trap_aging_slope_deep", channel="idle spells", est="ts1r_deep_beta", lo="ts1r_deep_ci[0]",
                 hi="ts1r_deep_ci[1]", level=0.95, ci_kind="percentile", n="ts1r_deep_events", n_kind="events",
                 method="agent-FE cloglog hazard slope on ln(elapsed), idle spells >= 10 min; day-block bootstrap",
                 null="memoryless band |slope| <= 0.3")])
spec(h="H17", src="H17-behavior-metastable-sets/G*/result.json", fmt="json", goal="folder",
     stats=[dict(statistic="implied_timescale_t2_min", channel="behavior", est="primary.t2", lo="primary.t2_ci[0]",
                 hi="primary.t2_ci[1]", level=0.95, ci_kind="percentile", n="primary.n_segments", n_kind="agent-days",
                 method="MSM implied timescale t2 at tau_c = 5 min (non-reversible MLE); agent-day bootstrap",
                 null="N2 sojourn-preserving null")])
spec(h="H18", src="H18-attention-dilution/summary.json", fmt="json_rows", rows="rows", goal="g",
     stats=[dict(statistic="dilution_exponent_beta", channel="D1 talk backlog", est="beta", lo="beta_lo", hi="beta_hi",
                 level=0.95, ci_kind="percentile", n="n_units", n_kind="units",
                 method="M_pow k^-beta logistic with agent x day propensities; agent-day bootstrap", null="beta = 0"),
            dict(statistic="dilution_exponent_beta", channel="D2 timer-wake", est="d2_beta", lo="d2_lo", hi="d2_hi",
                 level=0.95, ci_kind="percentile", n="d2_n", n_kind="units",
                 method="same fit on timer-wake batches (exogenous k)", null="beta = 0")])
spec(h="H19", src="H19-loop-gain-collapse/estimates.parquet", fmt="parquet", goal="goal_no",
     filter=lambda r: r["method"] in ("H19.geq_active", "H19.geq_talk"),
     stats=[dict(statistic="loop_gain_g_eq", channel="{method}", est="value", se="se", level=0.95, ci_kind="se_z",
                 n="n_days", n_kind="days",
                 method="Curie-Weiss 1 - 1/VR in 30-min blocks (H02 rules); day-bootstrap SE, IVW over 5-day chunks",
                 null=None)])
spec(h="H20", src="H20-content-aging/summary.json", fmt="json_rows", rows="rows", goal="g",
     stats=[dict(statistic="aging_slope_A", channel="content", est="A", n="N", n_kind="agents", ci_kind="none",
                 method="WLS of two-time content correlation on log t_w (aniso stationary null)",
                 null="parametric stationary null (pA)",
                 notes="H01 #38 kickoff-vector swap affects G38")])
spec(h="H22", src="H22-private-goals-spin-glass/G*/*/results.json", fmt="json", goal="folder", unit="parent_dir",
     filter=lambda r: r.get("unit") != "51D_standin",
     stats=[dict(statistic="mean_coupling_Jbar", channel="content", est="content.moments.Jbar",
                 lo="content.moments.Jbar_ci90[0]", hi="content.moments.Jbar_ci90[1]", level=0.90,
                 ci_kind="percentile", n="content.moments.N", n_kind="agents",
                 method="within-day content co-movement coupling; day bootstrap", null=None)])
spec(h="H25", src="H25-criticality-dial/dial_period.parquet", fmt="parquet", goal="goal_no",
     filter=lambda r: (r["channel"] in ("activity", "talk") and r["variant"] == "auto")
     or (r["channel"] == "content" and r["variant"] == "F2"),
     stats=[dict(statistic="loop_gain_g_daily_dial", channel="{channel}", est="fe", se="se_fe", level=0.90,
                 ci_kind="se_z", n="k", n_kind="days",
                 method="fixed-effect IVW mean of the daily Curie-Weiss dial g = 1 - 1/VR (stall-masked / F2 content)",
                 null=None)])
spec(h="H26", src="H26-content-near-critical/summary_units.json", fmt="json_list", goal="goal_no", unit="unit",
     stats=[dict(statistic="room_excess_gain_day", channel=ch, est=f"{p}_day_g", lo=f"{p}_day_g_ci[0]",
                 hi=f"{p}_day_g_ci[1]", level=0.95, ci_kind="percentile", n="n_days", n_kind="days",
                 method="drive-removed loop gain at day resolution: room excess if two_room else whole-room; day bootstrap",
                 null="N2 room permutation") for ch, p in (("content", "c"), ("activity", "a"), ("talk", "k"))])
spec(h="H28", src="H28-links-spread-herding/results_round1.parquet", fmt="parquet", goal="goal",
     filter=lambda r: bool(r["tested"]),
     stats=[dict(statistic="link_coupling_kappa", channel="project", est="kappa", se="se", level=0.95, ci_kind="se_z",
                 n="arrivals", n_kind="arrivals",
                 method="Poisson FE coefficient on a visible-link indicator; agent x day cluster-robust SE",
                 null="N1 link time-shift")])
spec(h="H29", src="H29-driver-nodes/G*/results.json", fmt="json", goal="folder", unit="folder",
     stats=[dict(statistic="net_pull_kappa", channel="content", est="kappa.kappa", lo="kappa.kappa_ci[0]",
                 hi="kappa.kappa_ci[1]", level=0.95, ci_kind="percentile", n="kappa.n_V", n_kind="message rows",
                 method="net content pull (visible minus placebo, minus invisible); day-block bootstrap",
                 null="invisible-message placebo")])
spec(h="H30", src="H30-operator-susceptibility/G*/results.json", fmt="json", goal="folder",
     stats=[dict(statistic="chi_act", channel=ch, est=f"act_nofe.{ch}[0]", lo=f"act_nofe.{ch}[1]", hi=f"act_nofe.{ch}[2]",
                 level=0.95, ci_kind="percentile", n=f"act_n.{ch}", n_kind="kicks",
                 method="extra active minutes in 30 min per kick (A30, strata, no day FE); day-block bootstrap",
                 null="day-swap null") for ch in ("N_tgt", "H_und")])
spec(h="H33", src="H33-diversity-productivity/results.json", fmt="json_rows", rows="per_period", goal="unit_goal",
     unit="unit", filter=lambda r: r.get("b1") is not None,
     stats=[dict(statistic=f"two_lines_slope_{k}", channel="content diversity", est=k, se=se, df="G-1", level=0.95,
                 ci_kind="se_t", n="n", n_kind="agent-days",
                 method="two-lines regression at pooled breakpoint PR10 = 15.97; agent + day FE; CR1 by agent",
                 null=f"{k} = 0") for k, se in (("b1", "se1"), ("b2", "se2"))])
spec(h="H34", src="H34-idea-cascades/results/period_table.parquet", fmt="parquet", goal="goal",
     filter=lambda r: r["cls"] == "ALL",
     stats=[dict(statistic="branching_ratio_R", channel="ideas", est="R", lo="R_lo", hi="R_hi", level=0.95,
                 ci_kind="percentile", n="nodes", n_kind="first uses",
                 method="children / nodes over idea trees; idea-cluster bootstrap", null="critical R = 1"),
            dict(statistic="exposure_hazard_ratio_HR10", channel="ideas", est="hr10", lo="hr10_lo", hi="hr10_hi",
                 level=0.95, ci_kind="profile", n="nodes", n_kind="first uses",
                 method="idea-stratified adoption hazard ratio within 10 min of a visible use", null="HR = 1 (field)")])
spec(h="H37", src="H37-stance-spins/G*/results.json", fmt="json", goal="folder",
     stats=[dict(statistic="negative_stance_share", channel="stance", est=p + ".f_neg",
                 lo=p + ".f_neg_ci90_dayboot[0]", hi=p + ".f_neg_ci90_dayboot[1]", level=0.90, ci_kind="percentile",
                 n=p + ".n_replies", n_kind="replies", method="share of replies labelled oppose (Jev zero-shot); day bootstrap",
                 null=None, notes="label-noise floor ~0.065") for p in ("detector", "primary")])
spec(h="H38", src="H38-platform-stalls/period_table.parquet", fmt="parquet", goal="goal_no",
     stats=[dict(statistic="excess_gain_raw", channel="activity", est="E_raw", n="days", n_kind="days", ci_kind="none",
                 method="g_raw (1 - 1/VR, 30-min blocks) minus the mean of 200 joint N1 surrogates",
                 null="N1 block shift (z_raw)"),
            dict(statistic="f_scaffold", channel="activity", est="f_mask_scaffold", n="days", n_kind="days",
                 ci_kind="none", method="1 - E_mask_scaffold / E_raw (agent-state conditioning)", null=None)])
spec(h="H39", src="H39-catalysts-vs-fields/G*/results.json", fmt="json", goal="folder", expand=("b4", "lever"),
     filter=lambda r, k=None: True,
     stats=[dict(statistic="catalytic_K", channel="{k}", est="b4.{k}.K", lo="b4.{k}.K_ci[0]", hi="b4.{k}.K_ci[1]",
                 level=0.95, ci_kind="percentile", n="b4.{k}.n_ep", n_kind="episodes", require="b4.{k}.status=ok",
                 method="ln ratio of occupancy-weighted escape, kicked vs matched control windows (W = 30); day bootstrap",
                 null="placebo episodes"),
            dict(statistic="field_phi", channel="{k}", est="b4.{k}.phi", lo="b4.{k}.phi_ci[0]", hi="b4.{k}.phi_ci[1]",
                 level=0.95, ci_kind="percentile", n="b4.{k}.n_ep", n_kind="episodes", require="b4.{k}.status=ok",
                 method="pi_C-weighted SD of delta ln pi; day bootstrap", null="placebo episodes")])
spec(h="H01", src="H01-emergent-superagents-exist/G*/results.json", fmt="json", goal="folder", expand=("P5_P6", "unit"),
     unit_from_key=True,
     stats=[dict(statistic="exposure_coupling_slope", channel="content", est="P5_P6.{k}.slope", se="P5_P6.{k}.slope_se",
                 level=0.95, ci_kind="se_z", n="P5_P6.{k}.n_pair_days", n_kind="pair-days",
                 method="pair fixed-effects OLS slope of residual alignment on log1p(exposure), rarefied vectors",
                 null="agent-rotation and day-shuffle nulls", notes="H01 #38 kickoff-vector swap affects G38")])
spec(h="H02", src="H02-couplings-are-real/mf_cw.parquet", fmt="parquet", goal="chunk", unit="chunk",
     stats=[dict(statistic="cw_beta_J0", channel="activity", est="bJ0", n="N", n_kind="agents", ci_kind="none",
                 method="Curie-Weiss inversion within (day, 30-min block): bJ0 = (1 - 1/VR)/q, per 5-day chunk",
                 null="N1 circular block-shift surrogates (z, p)")])
# period-native single-period designs
spec(h="H23", src="H23-leader-distillation-copy/G44/results.json", fmt="json", goal="folder",
     stats=[dict(statistic="leader_corpus_marker_rate", channel="content", est="O1.means.leader.r_corpus[0]",
                 lo="O1.means.leader.r_corpus[1]", hi="O1.means.leader.r_corpus[2]", level=0.95, ci_kind="percentile",
                 n="n.leader", n_kind="messages",
                 method="corpus-distinctive unigram + bigram hits per 100 tokens in the leader's messages; bootstrap",
                 null="control agents (O1.means.CTRL)", role="native")])
spec(h="H21", src="H21-debate-antiferromagnet/G12/results.json", fmt="json", goal="folder", role="native",
     stats=[dict(statistic="staggered_order_delta", channel="content", est="static.delta", lo="static.delta_ci[0]",
                 hi="static.delta_ci[1]", level=0.95, ci_kind="percentile", n="static.n_debates", n_kind="debates",
                 method="within-team minus cross-team cosine over #12's debates; debate bootstrap",
                 null="team permutation", role="native")])
spec(h="H24", src="H24-forecast-coupling-switch/G21/explore.json", fmt="json", goal="folder",
     stats=[dict(statistic="alignment_step_at_switch_on", channel="content", est="O1.n32_ghat.a_all.res.dA",
                 lo="O1.n32_ghat.a_all.res.boot.dA_ci90[0]", hi="O1.n32_ghat.a_all.res.boot.dA_ci90[1]", level=0.90,
                 ci_kind="percentile", n="O1.n32_ghat.a_all.res.N", n_kind="agents",
                 method="pre/post residual alignment step around each agent's switch-on; bootstrap",
                 null="within-week placebo", role="native")])


def _rows_of(sp) -> list:
    """(row dict, path, local unit, goal) tuples for a spec."""
    out = []
    for f in sorted(glob.glob(str(PROC / sp["src"]))):
        rel = str(Path(f).relative_to(ROOT))
        m = GOAL_RX.search(f)
        g_folder = int(m.group(1)) if m else None
        u_folder = (Path(f).parent.name[1:] if Path(f).parent.name.startswith("G") else None)
        if sp["fmt"] == "parquet":
            for r in pl.read_parquet(f).iter_rows(named=True):
                out.append((r, rel))
        elif sp["fmt"] == "json":
            d = json.loads(Path(f).read_text())
            d["_folder_goal"], d["_folder_unit"] = g_folder, u_folder
            d["_file_suffix"] = Path(f).stem.split("_", 1)[1] if "_" in Path(f).stem else None
            d["_file_u"] = Path(f).stem.split("_u", 1)[1] if "_u" in Path(f).stem else None
            d["_parent_dir"] = Path(f).parent.name
            out.append((d, rel))
        elif sp["fmt"] == "json_rows":
            d = json.loads(Path(f).read_text())
            for r in _get(d, sp["rows"]) or []:
                out.append((r, rel))
        elif sp["fmt"] == "json_list":
            for r in json.loads(Path(f).read_text()):
                out.append((r, rel))
    return out


def _goal(sp, r, k=None):
    g = sp["goal"]
    if g == "folder":
        return r.get("_folder_goal")
    if g == "{k}":
        return int(k)
    if g == "unit_goal":
        m = re.match(r"(\d+)", str(r.get("unit")))
        return int(m.group(1)) if m else None
    v = r.get(g)
    if isinstance(v, str):
        m = re.search(r"(\d+)", v)
        return int(m.group(1)) if m else None
    return None if v is None else int(v)


def _local_unit(sp, r):
    u = sp.get("unit")
    if u is None:
        return None
    if u == "folder":
        return r.get("_folder_unit")
    if u == "file_suffix":
        return r.get("_file_suffix")
    if u == "file_u":
        return r.get("_file_u")
    if u == "parent_dir":
        return r.get("_parent_dir")
    v = r.get(u)
    return None if v is None else str(v)


def backfill(verbose: bool = True) -> pl.DataFrame:
    rows = []
    for sp in B:
        for r, rel in _rows_of(sp):
            keys = [None]
            if sp.get("expand"):
                d = _get(r, sp["expand"][0])
                keys = sorted(d.keys()) if isinstance(d, dict) else []
            for k in keys:
                if sp.get("filter") is not None:
                    try:
                        if not sp["filter"](r):
                            continue
                    except (KeyError, TypeError):
                        continue
                goal = _goal(sp, r, k)
                if goal is None:
                    continue
                ul = str(k) if sp.get("unit_from_key") else _local_unit(sp, r)
                for st in sp["stats"]:
                    def P(path):
                        if path is None:
                            return None
                        path = path.replace("{k}", str(k)) if k is not None else path
                        return _get(r, path)
                    if st.get("require"):
                        pth, val = st["require"].split("=")
                        if str(P(pth)) != val:
                            continue
                    est = _num(P(st["est"]))
                    if est is None:
                        continue
                    lo, hi = _num(P(st.get("lo"))), _num(P(st.get("hi")))
                    se = _num(P(st.get("se")))
                    level = st.get("level")
                    if se is not None and lo is None:
                        df_ = st.get("df")
                        if isinstance(df_, str) and df_.endswith("-1"):
                            df_ = (_num(P(df_[:-2])) or 2) - 1
                        lo, hi = ci_from_se(est, se, level or 0.95, df_ if st.get("ci_kind") == "se_t" else None)
                    if lo is not None and hi is not None and lo > hi:
                        lo, hi = hi, lo
                    ch = st.get("channel")
                    if callable(ch):
                        ch = ch(r, k)
                    elif ch and "{" in ch:
                        ch = ch.replace("{k}", str(k)) if k is not None else re.sub(
                            r"\{(\w+)\}", lambda mm: str(r.get(mm.group(1))), ch)
                    pu = map_unit(goal) if ul is None or ul in (str(goal), f"{goal:02d}") else ""
                    if not pu:
                        pu = f"local:{ul}" if ul else f"G{goal:02d}"
                    nval = _num(P(st.get("n")))
                    mt = dt.datetime.fromtimestamp((ROOT / rel).stat().st_mtime, dt.timezone.utc).isoformat()
                    rows.append({"hypothesis": sp["h"], "period_unit": pu, "goal_no": goal, "statistic": st["statistic"],
                                 "channel": ch, "estimate": est, "ci_lo": lo, "ci_hi": hi, "n": nval,
                                 "method": st["method"], "null": st.get("null"),
                                 "role": st.get("role", sp.get("role", "replication")), "ci_level": level,
                                 "ci_kind": st.get("ci_kind", "percentile" if lo is not None else "none"), "se": se,
                                 "n_kind": st.get("n_kind"), "unit_local": ul, "post_hoc": bool(st.get("post_hoc", False)),
                                 "status": "backfilled", "source": rel, "source_mtime": mt, "notes": st.get("notes")})
    df = complete(_frame(rows))
    # held-out periods never appear in these exploratory sources; keep the guard explicit
    held = df.filter(pl.col("holdout"))
    if held.height:
        print(f"WARNING: dropping {held.height} held-out rows from the backfill: "
              f"{held.select('hypothesis', 'period_unit').unique().rows()}")
        df = df.filter(~pl.col("holdout"))
    errs = validate(df)
    if errs:
        raise ValueError("; ".join(errs))
    return df


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    a = ap.parse_args()
    if a.backfill:
        df = backfill()
        old = read_estimates()
        if old.height:   # keep rows written by hypotheses themselves; replace earlier backfills
            old = old.filter(pl.col("status") != "backfilled")
        out = pl.concat([old, df]).sort("hypothesis", "statistic", "goal_no", "period_unit")
        out.write_parquet(PATH, compression="zstd")
        from common import write_provenance
        srcs = sorted(df["source"].unique().to_list())
        write_provenance("estimates", ["(hypothesis outputs, read-only)"] + srcs,
                         {"n_rows": out.height, "n_backfilled": df.height, "specs": len(B)})
        prov = json.loads((OUT / "_provenance.json").read_text())
        prov["per_period_estimates"] = prov.pop("estimates")
        prov["per_period_estimates"]["built_by"] = "infra/shared/estimates.py --backfill"
        (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
        a.coverage = True
    if a.coverage:
        df = read_estimates()
        cov = (df.group_by("hypothesis", "statistic", "role").agg(pl.len().alias("rows"),
                                                                   pl.col("goal_no").n_unique().alias("periods"),
                                                                   pl.col("ci_lo").is_not_null().mean().alias("with_ci"))
               .sort("hypothesis", "statistic"))
        with pl.Config(tbl_rows=200, tbl_width_chars=200, float_precision=2):
            print(cov)
        print(f"rows {df.height}, hypotheses {df['hypothesis'].n_unique()}, periods {df['goal_no'].n_unique()}, "
              f"statistics {df.select('hypothesis', 'statistic').unique().height}")


if __name__ == "__main__":
    main()
