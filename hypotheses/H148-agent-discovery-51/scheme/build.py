"""H148 scheme: atom panels for autonomous agent discovery in #51 (2026-07-06 -> 09-04; 51m reserved and masked;
#45-#50 not used).

Builds data/processed/H148-agent-discovery-51/:
  bins_<w>.parquet     one row per bin (w = 30, 120 min; 1440 = one bin per day): day, bin in day, valid flag, E parts
  atoms_<w>.npz        S (n_atoms x n_bins int8 states), K (alphabet per atom), present (agents x bins), resets, meta
  atoms.parquet        atom table: atom, kind (agent / artifact / room), name, agent, owner, K, labels, own_of, shared
  agent_activity.parquet  per agent x day: non-pause calls, touching calls (for nulls and KW scrambles)
  commits_clean.parquet   the cleaned work commits used for artifact atoms (slug, t, author; no hashes, no text)
  _provenance.json
Element atoms (H145's frozen elements) are added by analysis/elements.py after scratchpad/H145.READY.

Bins and presence: `infra/shared/memeplex.py: make_bins` (16:00 UTC anchor, 8 h per day, DQ8 per-agent presence
trim: present when the agent's first-to-last non-pause call span covers >= half of the bin). A bin is valid when >= 1
agent is present. Same bins as H145's expression panels, so element atoms line up.

Atom states (card "Building blocks"; Round 1 amendment A2 drops the content cluster from the agent state):
  agent    0 not present | 1 present, no project touch | 2 own top project | 3 second project | 4 other
           (modal touched project of the agent's non-pause calls in the bin, `project_calls.proj` mapped to repo
           slugs with `memeplex.slug`; never `label`, which carries over resets). Top projects from the whole span.
  artifact 0 not written | 1 written by its owner only | 2 written by a non-owner (cleaned work commits).
           Artifacts: each agent's own repo (its most-committed repo, >= 10 commits) and shared repos (>= 3 writers
           with >= 3 commits each).
  room     0 no agent message | 1 low talk | 2 high talk (#general room 0, #focus room 15; split at the room's median
           nonzero count).
E parts per bin (lagged in the analysis): phase (0 first bin of the day, 1 middle, 2 last), exogenous input in the
bin (human message, automated operator message: nudge, pause/resume, kickoff; relayed human input in Claude Fable 5's
and others' messages, from H145's exo.parquet E table), rest-of-village present-agent count (computed per system in
the analysis, the system's own agents removed).

Data traps (run brief): `memeplex.clean_commits` (since 4f6ab2e: automated commits dropped; the
surprise-lab-mirror-proofs repo dropped by name; busy single-file streams kept, which are the Echoes pair's chapter
commits; commits by agents with no touching call on the repo that day dropped, which removes the other village's
'-chat' identities; hash dedupe; commits before the author joined dropped). Pause and wait calls are not activity.
Claude Code agents are not in the panel (make_bins).

Usage: uv run python hypotheses/H148-agent-discovery-51/scheme/build.py [--verify]
"""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402
import memeplex as MP  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H148-agent-discovery-51"
EXO = ROOT / "data/processed/H145-ideology-egregores-51/exo.parquet"
GOAL = 51
FOCUS_ROOM, GENERAL_ROOM = 15, 0
NONACT = ("pause", "wait")
WIDTHS = (30, 120, 1440)
LAST_DAY = "2026-09-04"


def locate_bins(bins: MP.Bins, t: np.ndarray) -> np.ndarray:
    """Bin index for timestamps (-1 outside the bins)."""
    t = np.asarray(t).astype("datetime64[us]")
    w = np.timedelta64(MP.DAY_HOURS * 60 if bins.width_min >= 1440 else bins.width_min, "m")
    pos = np.searchsorted(bins.t0, t, side="right") - 1
    ok = (pos >= 0) & (t < bins.t0[np.clip(pos, 0, None)] + w)
    return np.where(ok, pos, -1)


def load_calls(days: list[str]) -> pl.DataFrame:
    pc = (pl.scan_parquet(SH / "project_calls.parquet")
          .filter((pl.col("goal_no") == GOAL) & (~pl.col("holdout")) & pl.col("pt_date").is_in(days))
          .select("agent", "pt_date", "kind", "t_call", "proj")
          .collect())
    u = pc["proj"].drop_nulls().unique().to_list()
    lut = pl.DataFrame({"proj": u, "slug": [MP.slug(p) for p in u]})
    return (pc.join(lut, on="proj", how="left")
            .with_columns((~pl.col("kind").cast(pl.String).is_in(NONACT)).alias("act")))


def main(verify: bool = False):
    OUT.mkdir(parents=True, exist_ok=True)
    days = [d for d in MP.period_days(GOAL) if d <= LAST_DAY]
    assert not any(holdout_mask(days, [GOAL] * len(days)))
    roster = pl.read_parquet(SH / "roster.parquet")
    names = dict(zip(roster["agent"].to_list(), roster["name"].to_list()))
    calls = load_calls(days)
    clog = {}
    commits = MP.clean_commits(GOAL, clog).filter(pl.col("pt_date").is_in(days))
    clog["kept_in_span"] = commits.height
    commits.select("slug", "t", "pt_date", "author_agent").write_parquet(OUT / "commits_clean.parquet",
                                                                          compression="zstd")
    b120 = MP.make_bins(GOAL, 120, days)
    agents = list(b120.agents)
    # --- atom definitions (whole non-reserved span; definitions, not outcomes)
    top = (calls.filter(pl.col("act") & pl.col("slug").is_not_null() & pl.col("agent").is_in(agents))
           .group_by("agent", "slug").len().sort(["agent", "len", "slug"], descending=[False, True, False]))
    top_proj = {a: top.filter(pl.col("agent") == a)["slug"].head(2).to_list() for a in agents}
    wc_ag = (commits.filter(pl.col("author_agent").is_in(agents)).group_by("slug", "author_agent").len()
             .sort(["slug", "len", "author_agent"], descending=[False, True, False]))
    own = {}
    for a in agents:
        r = wc_ag.filter(pl.col("author_agent") == a).sort(["len", "slug"], descending=[True, False])
        if r.height and r["len"][0] >= 10:
            own[a] = r["slug"][0]
    writers = wc_ag.filter(pl.col("len") >= 3).group_by("slug").agg(pl.len().alias("nw"))
    shared = sorted(writers.filter(pl.col("nw") >= 3)["slug"].to_list())
    art = sorted(set(own.values()) | set(shared))
    owner = {s: int(wc_ag.filter(pl.col("slug") == s)["author_agent"][0]) for s in art}
    atoms = []
    for a in agents:
        tp = top_proj[a]
        atoms.append({"kind": "agent", "name": names[a], "agent": a, "owner": a, "K": 5,
                      "labels": json.dumps(["absent", "present", tp[0] if tp else "-", tp[1] if len(tp) > 1 else "-",
                                            "other"]), "own_of": "[]", "shared": False})
    for s in art:
        atoms.append({"kind": "artifact", "name": s, "agent": -1, "owner": owner[s], "K": 3,
                      "labels": json.dumps(["none", "owner", "non-owner"]),
                      "own_of": json.dumps(sorted(int(a) for a, v in own.items() if v == s)),
                      "shared": s in shared})
    for nm in ("#general", "#focus"):
        atoms.append({"kind": "room", "name": nm, "agent": -1, "owner": -1, "K": 3,
                      "labels": json.dumps(["none", "low", "high"]), "own_of": "[]", "shared": False})
    at = pl.DataFrame(atoms, infer_schema_length=None).with_row_index("atom").with_columns(
        pl.col("atom").cast(pl.Int16), pl.col("agent").cast(pl.Int16), pl.col("owner").cast(pl.Int16),
        pl.col("K").cast(pl.Int8))
    at.write_parquet(OUT / "atoms.parquet")

    chat = (pl.scan_parquet(SH / "chat_core.parquet")
            .filter((pl.col("goal_no") == GOAL) & pl.col("pt_date").is_in(days) & (pl.col("speaker_kind") == "agent")
                    & pl.col("room").is_in([GENERAL_ROOM, FOCUS_ROOM]))
            .select("t", "room").collect())
    exo = pl.read_parquet(EXO).filter(pl.col("pt_date").is_in(days)).select("t", "src")
    resets = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
              .filter((pl.col("goal_no") == GOAL) & (~pl.col("holdout")) & pl.col("pt_date").is_in(days)
                      & pl.col("reset_forced"))
              .select("agent", "t_call").collect())
    aidx = {a: i for i, a in enumerate(agents)}
    sidx = {s: i for i, s in enumerate(art)}
    nA, nR = len(agents), len(art)
    act = calls.filter(pl.col("act") & pl.col("agent").is_in(agents))
    prov_bins = {}
    for w in WIDTHS:
        bins = MP.make_bins(GOAL, w, days)
        assert list(bins.agents) == agents
        nB = bins.nB
        pres = bins.present
        S = np.zeros((at.height, nB), np.int8)
        S[:nA] = pres.astype(np.int8)
        # agents: modal touched project among non-pause calls in the bin (present bins only)
        b = locate_bins(bins, act["t_call"].to_numpy())
        cb = act.with_columns(pl.Series("bin", b)).filter((pl.col("bin") >= 0) & pl.col("slug").is_not_null())
        mod = (cb.group_by("agent", "bin", "slug").len()
               .sort(["agent", "bin", "len", "slug"], descending=[False, False, True, False])
               .group_by("agent", "bin", maintain_order=True).first())
        for a, bb, s, _ in mod.iter_rows():
            i = aidx[a]
            if not pres[i, bb]:
                continue
            tp = top_proj[a]
            S[i, bb] = 2 if (tp and s == tp[0]) else 3 if (len(tp) > 1 and s == tp[1]) else 4
        # artifacts
        cm = commits.filter(pl.col("slug").is_in(art))
        b = locate_bins(bins, cm["t"].to_numpy())
        for s, bb, aa in zip(cm["slug"].to_list(), b.tolist(), cm["author_agent"].to_list()):
            if bb < 0:
                continue
            i = nA + sidx[s]
            S[i, bb] = max(S[i, bb], 1 if aa == owner[s] else 2)
        # rooms
        b = locate_bins(bins, chat["t"].to_numpy())
        rm = chat["room"].to_numpy()
        for j, room in enumerate((GENERAL_ROOM, FOCUS_ROOM)):
            ok = (b >= 0) & (rm == room)
            v = np.bincount(b[ok], minlength=nB).astype(float)
            nz = v[v > 0]
            med = np.median(nz) if nz.size else 0
            S[nA + nR + j] = np.where(v == 0, 0, np.where(v <= med, 1, 2))
        # E parts
        valid = pres.any(0)
        dob = bins.day_of_bin
        phase = np.ones(nB, np.int8)
        for d in np.unique(dob):
            ix = np.flatnonzero((dob == d) & valid)
            if ix.size:
                phase[ix[0]] = 0
                phase[ix[-1]] = 2
        ex = np.zeros(nB, np.int8)
        b = locate_bins(bins, exo["t"].to_numpy())
        ex[np.unique(b[b >= 0])] = 1
        exh = np.zeros(nB, np.int8)          # human or relayed human input only
        hb = b[(b >= 0) & (exo["src"].to_numpy() != "automated")]
        exh[np.unique(hb)] = 1
        R = np.zeros((nA, nB), np.int16)
        b = locate_bins(bins, resets["t_call"].to_numpy())
        for a, bb in zip(resets["agent"].to_list(), b.tolist()):
            if bb >= 0 and a in aidx:
                R[aidx[a], bb] += 1
        g = pl.DataFrame({"bin": np.arange(nB, dtype=np.int32), "pt_date": [bins.days[d] for d in dob],
                          "day": dob.astype(np.int16), "k": bins.bin_in_day.astype(np.int16),
                          "t0": bins.t0, "valid": valid, "phase": phase, "exog": ex, "exog_h": exh,
                          "n_present": pres.sum(0).astype(np.int16)})
        g.write_parquet(OUT / f"bins_{w}.parquet")
        actv = (S > 0)[:, valid].sum(1)
        np.savez_compressed(OUT / f"atoms_{w}.npz", S=S, K=at["K"].to_numpy(), activity=actv, resets=R,
                            present=pres, agents=np.array(agents))
        prov_bins[w] = {"n_bins": nB, "n_valid": int(valid.sum()), "n_exog_bins": int(ex.sum()),
                       "n_exog_h_bins": int(exh.sum())}
        print(f"width {w}: bins {nB}, valid {valid.sum()}, exog bins {ex.sum()}, human/relayed {exh.sum()}", flush=True)
    aa = calls.group_by("agent", "pt_date").agg(pl.col("act").sum().alias("n_act"), pl.len().alias("n_calls"),
                                                pl.col("slug").is_not_null().sum().alias("n_touch"))
    aa.write_parquet(OUT / "agent_activity.parquet")
    commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True,
                            text=True).stdout.strip()
    rev = ""
    src = ROOT / "data/raw/ai-village/_source.md"
    if src.exists():
        for ln in src.read_text().splitlines():
            if "revision" in ln.lower():
                rev = ln.strip()
                break
    prov = {"built_by": "hypotheses/H148-agent-discovery-51/scheme/build.py", "git_commit": commit,
            "inputs": [{"source": "ai-village", "revision": rev or "see data/raw/ai-village/_source.md",
                        "tables": ["calendar", "project_calls", "call_windows", "project_call_touches",
                                   "work_commits", "roster", "chat_core", "context_ledger_turns"]},
                       {"source": "H145-ideology-egregores-51", "tables": ["exo.parquet (E: exogenous input)"]}],
            "params": {"goal": GOAL, "days": [days[0], days[-1]], "n_days": len(days), "widths": list(WIDTHS),
                       "commit_cleaning": clog, "n_agents": nA, "n_artifacts": nR, "artifacts": art,
                       "own_repo": {names[a]: s for a, s in own.items()}, "shared_repos": shared,
                       "bins": prov_bins,
                       "reserved": "51m masked by holdout_mask; days after 2026-09-04 excluded; #45-#50 not read"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(json.dumps(clog), nA, "agents", nR, "artifacts", len(shared), "shared")
    if verify:
        z = np.load(OUT / "atoms_30.npz")
        S = z["S"]
        assert S.max() < 5 and S.min() >= 0
        assert days[-1] <= LAST_DAY and len(days) >= 40
        assert ((S[:nA] > 0) == z["present"]).all()
        print("verify ok")


if __name__ == "__main__":
    main(verify="--verify" in sys.argv)
