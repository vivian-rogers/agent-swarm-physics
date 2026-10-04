"""Load the H01 scheme into per-unit `Unit` objects (non-holdout only; asserted).

Goal field g-hat (per unit): unit(unit(goal text) + unit(mean kickoff)), whitened in the unit's regime basis.
Room field g-hat_r: same with the room's own kickoff. Agent goal field (#51 units): the agent's assigned goal valid
on most of the unit's days. Agent field h_i (cross-fitted): unit mean of agent i's unit agent-day vectors over
non-holdout days of OTHER goal periods in the same regime; if none, other sub-units of the same goal period;
if none, the agent's first day in the unit (then its pairs on that day are dropped). See the card, Amendment 2.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h01common import OUT, SH, guard_holdout, load_basis, unit, whiten_apply  # noqa: E402
from h01lib import Unit  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

P56_UNITS = ["35", "36b", "37", "38a", "38b", "38c", "39", "40", "41", "42", "44", "51a", "51b", "51c", "51d", "51e"]
P1_UNITS = ["35", "38a", "38b", "38c", "39", "40", "41", "42", "44", "51c"]     # card list (#40: merged, see notes)
P1_EXTRA = ["36b", "37"]                                                        # regime III two-room units not in the card list


class Scheme:
    def __init__(self, d=32, allow_holdout=False, base=OUT, shared_room_kickoffs=True):
        self.base = Path(base)
        self.d = d
        self.st = pl.read_parquet(self.base / "statements.parquet").with_row_index("row")
        guard_holdout(sorted(self.st["pt_date"].unique().to_list()), allow=allow_holdout)
        Z = np.load(self.base / "vectors_w64.npy").astype(np.float32)
        self.U = unit(Z[:, :d]).astype(np.float32)
        cl = pl.read_parquet(self.base / "clusters.parquet")
        self.labels = {20: cl["k20"].to_numpy(), 40: cl["k40"].to_numpy(), 80: cl["k80"].to_numpy()}
        if d == 16:
            self.labels = {40: cl["k40_d16"].to_numpy()}
        elif d == 64:
            self.labels = {40: cl["k40_d64"].to_numpy()}
        self.ad = pl.read_parquet(self.base / "agent_day.parquet")
        self.units = {u["unit"]: u for u in json.loads((self.base / "units.json").read_text())}
        self.goals = pl.read_parquet(self.base / "goals.parquet")
        self.graw = np.load(self.base / "goals_raw.npy").astype(np.float32)
        self.room_kickoff_source = "h01 goals_raw.npy (uncorrected)"
        if shared_room_kickoffs and self.graw.shape[1] == 384:
            self._shared_room_kickoffs()
        self.bases = {}
        for R in ("I", "II", "III"):
            f = self.base / f"basis_{R}.npz"
            if f.exists():
                z = np.load(f); self.bases[R] = {k: z[k] for k in z.files}
        ex = pl.read_parquet(self.base / "pair_day_exposure.parquet")
        self.E = {(d_, i, j): n for d_, i, j, n in ex.iter_rows()}
        ro = pl.read_parquet(SH / "roster.parquet")
        self.lab_of = dict(zip(ro["agent"].to_list(), ro["lab"].to_list()))
        self.name_of = dict(zip(ro["agent"].to_list(), ro["name"].to_list()))
        # agent-day vectors at dim d, keyed (agent, pt_date)
        g = self.st.group_by("agent", "pt_date", maintain_order=True).agg(pl.col("row"), pl.col("unit").first(),
                                                                          pl.col("goal_no").first(), pl.col("regime").first())
        self.adrows = {(a, dd): np.array(r) for a, dd, r, *_ in g.iter_rows()}
        self.adinfo = g.drop("row")
        self.adV = {k: unit(self.U[v].mean(0)) for k, v in self.adrows.items()}

    # ------------------------------------------------------------------ fields
    def _shared_room_kickoffs(self):
        """Correction 2026-10-04 (found by the shared-pipeline consolidation): per-room kickoff vectors are read from the
        shared goal table (infra/shared/goal_fields.py, kind = kickoff_room; data/processed/shared/embeddings/). H01's own
        goals_raw.npy had the #38 room-2 and room-3 kickoff rows swapped (a --reuse-goal-emb reload of vectors saved
        under a different group_by order in scheme/build.py); all other kickoff rows match the shared table at
        cos >= 0.999. Only the room-field robustness variant (field_basis(use_room=True)) uses these rows; the
        period-level g-hat averages the room kickoffs and is unchanged by a label swap. Only for the bge instrument."""
        sg = pl.read_parquet(SH / "embeddings/goals.parquet")
        sv = np.load(SH / "embeddings/goal_vectors.npy").astype(np.float32)
        n = 0
        for r in self.goals.filter(pl.col("kind") == "kickoff").iter_rows(named=True):
            m = sg.filter((pl.col("goal_no") == r["goal_no"]) & (pl.col("kind") == "kickoff_room") & (pl.col("room") == r["room"]))
            if m.height:
                self.graw[r["gid"]] = sv[int(m["gid"][0])]
                n += 1
        self.room_kickoff_source = f"shared goals table ({n} kickoff_room rows)"

    def _gvec(self, gid, regime):
        b = self.bases[regime]
        return unit(whiten_apply(self.graw[gid:gid + 1], b, self.d)[0])

    def ghat(self, goal_no, regime):
        g = self.goals.filter((pl.col("goal_no") == goal_no) & (pl.col("regime") == regime))
        gg = g.filter(pl.col("kind") == "goal")["gid"].to_list()
        kk = g.filter(pl.col("kind") == "kickoff")
        vg = self._gvec(gg[0], regime)
        out = {"goal": vg, "kick": None, "room": {}}
        if kk.height:
            vk = unit(np.mean([self._gvec(i, regime) for i in kk["gid"].to_list()], 0))
            out["kick"] = vk
            out["ghat"] = unit(vg + vk)
            for r, gid in zip(kk["room"].to_list(), kk["gid"].to_list()):
                out["room"][r] = unit(vg + self._gvec(gid, regime))
        else:
            out["ghat"] = vg
        return out

    def agent_goals(self, days, regime):
        g = self.goals.filter((pl.col("kind") == "agent_goal") & (pl.col("regime") == regime))
        res = {}
        for a in g["agent"].unique().to_list():
            best, bestn = None, 0
            for r in g.filter(pl.col("agent") == a).iter_rows(named=True):
                n = sum((r["valid_from"] is None or d >= r["valid_from"]) and (r["valid_to"] is None or d <= r["valid_to"]) for d in days)
                if n > bestn:
                    best, bestn = r["gid"], n
            if best is not None:
                res[a] = self._gvec(best, regime)
        return res

    def h_crossfit(self, unit_name, agents, regime, days):
        ui = self.units[unit_name]
        info = self.adinfo.filter(pl.col("regime") == regime)
        h, first = {}, set()
        for a in agents:
            ia = info.filter(pl.col("agent") == a)
            other = ia.filter(pl.col("goal_no") != ui["goal_no"])
            src = "other_period"
            if other.height == 0:
                other = ia.filter((pl.col("goal_no") == ui["goal_no"]) & (pl.col("unit") != unit_name))
                src = "other_subunit"
            if other.height == 0:
                mine = sorted(d for d in ia.filter(pl.col("unit") == unit_name)["pt_date"].to_list() if d in days)
                if len(mine) < 2:
                    continue
                h[a] = self.adV[(a, mine[0])]; first.add(a)
                continue
            h[a] = unit(np.mean([self.adV[(a, d)] for d in other["pt_date"].to_list()], 0))
        return h, first

    # ------------------------------------------------------------------ units
    def h_firstday(self, agents_days):
        """Amendment 1 fallback: h_i = the agent's first day in the unit (that day is then dropped from pair tests)."""
        h, first = {}, set()
        for a, ds in agents_days.items():
            ds = sorted(ds)
            if len(ds) >= 2:
                h[a] = self.adV[(a, ds[0])]; first.add(a)
        return h, first

    def unit(self, name, use_agent_goals=True, days=None, label_override=None, h_mode="firstday"):
        ui = self.units[name]
        days = ui["days"] if days is None else days
        regime = ui["regimes"][-1] if len(ui["regimes"]) == 1 else ui["regimes"][0]
        a_ = self.ad.filter(pl.col("pt_date").is_in(days) & (pl.col("unit") == name)).sort("pt_date", "agent")
        agents = a_["agent"].to_numpy(); dmap = {d: i for i, d in enumerate(days)}
        day = np.array([dmap[d] for d in a_["pt_date"].to_list()])
        room = a_["room_mode"].fill_null(-1).to_numpy()
        rows = [self.adrows[(a, d)] for a, d in zip(agents, a_["pt_date"].to_list())]
        V = np.stack([self.adV[(a, d)] for a, d in zip(agents, a_["pt_date"].to_list())])
        E = {(dmap[d], i, j): n for (d, i, j), n in self.E.items() if d in dmap}
        gh = self.ghat(ui["goal_no"], regime)
        if h_mode == "crossfit":
            h, first = self.h_crossfit(name, np.unique(agents), regime, days)
        else:
            adays = {}
            for a, d in zip(agents, a_["pt_date"].to_list()):
                adays.setdefault(a, []).append(d)
            h, first = self.h_firstday(adays)
        ga = self.agent_goals(days, regime) if (use_agent_goals and ui["goal_no"] == 51) else {}
        ga = {a: v for a, v in ga.items() if a in set(agents)}
        lab = self.labels if label_override is None else label_override
        return Unit(name=name, agents=agents, day=day, room=room, V=V, nstmt=a_["n_stmt"].to_numpy(), rows=rows,
                    U=self.U, lab=lab, E=E, ghat=gh["ghat"], h=h, ghat_room=gh["room"], ghat_agent=ga, h_firstday=first,
                    labs={a: self.lab_of.get(a) for a in np.unique(agents)}, day_names=list(days))
