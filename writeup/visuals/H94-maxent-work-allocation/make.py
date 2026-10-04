"""H94 writeup visual: work is allocated at maximum entropy given activity, repo sizes, ownership and rooms.

Builds fig.pdf / fig.png from data/processed/H94-maxent-work-allocation/ (quanta + results JSONs):
  (a-c) a shared week (#41): observed agent x repo work quanta, max-ent with margins only (M1), max-ent with
        margins + ownership + rooms (M3);
  (d-f) a private-role unit (51d): observed, M1, max-ent with margins + ownership (M2);
  (g)   ownership price lambda_own per testable unit (agent-bootstrap 95% CI), shared vs own-role units;
  (h)   where I(agent; repo) goes per unit: ownership, rooms, residual above the run-persistence floor, floor.
The max-ent fits are recomputed with the card's own estimator (h94lib.hierarchy); lambda, shares and floors are read
from results/G<NN>.json. Usage: uv run python writeup/visuals/H94-maxent-work-allocation/make.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "writeup/visuals"))
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(ROOT / "hypotheses/H94-maxent-work-allocation/analysis"))
import vstyle as vs  # noqa: E402
from common import holdout_mask  # noqa: E402
import h94lib as L  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import PowerNorm  # noqa: E402

D = ROOT / "data/processed/H94-maxent-work-allocation"
SHARED = ["31a", "33", "35", "36c", "38a", "40", "41"]


def load_unit(g: int, unit: str):
    q = pl.read_parquet(D / f"G{g:02d}" / "quanta.parquet")
    assert not any(holdout_mask(q["pt_date"].to_list(), [g] * q.height)), "held-out rows"
    q = q.filter(pl.col("unit").cast(pl.Utf8) == unit)
    two = q["room_mode"].drop_nulls().n_unique() > 1
    labs = dict(pl.read_parquet(ROOT / "data/processed/shared/roster.parquet", columns=["agent", "lab"]).iter_rows())
    t = L.unit_table(q, "own", labs)
    h = L.hierarchy(t, two)
    return t, h, two


def order(t):
    """Agents by activity; repos grouped by owner (in agent order), then by size: ownership shows as a diagonal."""
    n = t["n"]
    ai = np.argsort(-n.sum(1))
    rank = {a: k for k, a in enumerate(ai)}
    owner = np.array([np.flatnonzero(t["own"][:, j])[0] if t["own"][:, j].any() else -1 for j in range(n.shape[1])])
    key = [(rank.get(o, 999) if o >= 0 else 999, -n[:, j].sum()) for j, o in enumerate(owner)]
    rj = sorted(range(n.shape[1]), key=lambda j: key[j])
    return ai, np.array(rj)


def heat(ax, M, t, ai, rj, vmax, title, show_own=True):
    X = M[np.ix_(ai, rj)] / M.sum()
    im = ax.imshow(X, cmap=vs.SEQ, norm=PowerNorm(0.5, vmin=0, vmax=vmax), aspect="auto", interpolation="nearest")
    if show_own:
        oi, oj = np.nonzero(t["own"][np.ix_(ai, rj)])
        ax.scatter(oj, oi, s=1.6, color=vs.C["orange"], marker="s", lw=0)
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(True); s.set_color(vs.GRID)
    ax.set_title(title, fontsize=7, loc="left")
    return im


def all_units():
    rows = []
    for f in sorted((D / "results").glob("G*.json")):
        for u, r in json.loads(f.read_text())["units"].items():
            if r.get("testable"):
                rows.append(dict(unit=u, own_unit=r["own_unit"], lam=r["lam_own"], lo=r["lam_own_lo"], hi=r["lam_own_hi"],
                                 own=r["own_share"], room=r["room_share"] or 0.0, res=r["resid_share_persist"],
                                 D1=r["D1"]))
    return rows


def main():
    vs.use()
    fig = plt.figure(figsize=(vs.W["double"], 4.5))
    gs = fig.add_gridspec(2, 5, width_ratios=[1, 1, 1, 0.42, 1.9], hspace=0.42, wspace=0.12)
    cases = [(41, "41", "#41 shared week\n13 agents × 26 repos", "M3"), (51, "51d", "51d private roles\n24 agents × 31 repos", "M2")]
    res = json.loads((D / "results/G41.json").read_text())["units"]["41"], json.loads((D / "results/G51.json").read_text())["units"]["51d"]
    for row, ((g, u, name, mk), rr) in enumerate(zip(cases, res)):
        t, h, two = load_unit(g, u)
        assert abs(h["D1"] - rr["D1"]) < 1e-6 and abs(h["lam_own"] - rr["lam_own"]) < 1e-6, "refit does not match results"
        mu = h["_mu"]
        ai, rj = order(t)
        vmax = float((t["n"] / t["n"].sum()).max())
        lab0 = "abc"[0] if row == 0 else "def"[0]
        letters = ("a", "b", "c") if row == 0 else ("d", "e", "f")
        ax0 = fig.add_subplot(gs[row, 0]); heat(ax0, t["n"], t, ai, rj, vmax, f"({letters[0]}) observed")
        ax0.set_ylabel(name, fontsize=7)
        ax1 = fig.add_subplot(gs[row, 1])
        heat(ax1, mu["M1"], t, ai, rj, vmax, f"({letters[1]}) max-ent: margins")
        ax1.text(0.97, 0.03, f"{h['D1']:.2f} bit/q left", transform=ax1.transAxes, ha="right", va="bottom",
                 fontsize=5.5, color=vs.INK, bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.8))
        ax2 = fig.add_subplot(gs[row, 2])
        im = heat(ax2, mu[mk], t, ai, rj, vmax,
                  f"({letters[2]}) + ownership" + (" + rooms" if mk == "M3" else ""))
        Dk = h["D3"] if mk == "M3" else h["D2"]
        ax2.text(0.97, 0.03, f"{Dk:.2f} bit/q left", transform=ax2.transAxes, ha="right", va="bottom",
                 fontsize=5.5, color=vs.INK, bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.8))
        ax0.text(0.0, -0.09, "repos, grouped by owner", transform=ax0.transAxes, fontsize=5.5, color=vs.INK2, va="top")
    cax = fig.add_axes([0.06, 0.035, 0.18, 0.012])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.set_label("share of the unit's work quanta (sqrt scale)", fontsize=5.5); cb.ax.tick_params(labelsize=5)
    fig.text(0.27, 0.03, "orange squares: owner's own repo", fontsize=5.5, color=vs.INK2, va="center")

    rows = all_units()
    # (g) lambda_own
    ax = fig.add_subplot(gs[0, 4])
    sh = [r for r in rows if not r["own_unit"]]; ow = [r for r in rows if r["own_unit"]]
    sh.sort(key=lambda r: r["lam"]); ow.sort(key=lambda r: r["lam"])
    for k, (grp, col, mk, x0) in enumerate(((sh, vs.C["sky"], "o", 0), (ow, vs.C["orange"], "s", len(sh) + 1))):
        xs = x0 + np.arange(len(grp))
        lam = np.array([r["lam"] for r in grp]); lo = np.array([r["lo"] for r in grp]); hi = np.array([r["hi"] for r in grp])
        ax.vlines(xs, np.minimum(lo, lam), np.maximum(hi, lam), color=col, lw=1.0, alpha=0.8)
        ax.scatter(xs, lam, marker=mk, s=12, color=col, edgecolor="white", lw=0.3, zorder=3)
        med = float(np.median(lam))
        ax.hlines(med, xs[0] - 0.4, xs[-1] + 0.4, color=vs.INK2, lw=0.8, ls="--")
        meds = locals().setdefault("meds", []); meds.append(med)
        for x, r in zip(xs, grp):
            if r["unit"] in ("40", "39"):
                ax.text(x, r["lam"] + 0.9, "#" + r["unit"], fontsize=5, ha="center", color=vs.INK2)
    ax.axhline(L.CAP, color=vs.MUTED, lw=0.6, ls=":")
    ax.text(-0.6, L.CAP + 0.3, "separation cap", fontsize=5.5, color=vs.MUTED, ha="left", va="bottom")
    ax.set_xticks([(len(sh) - 1) / 2, len(sh) + 1 + (len(ow) - 1) / 2], [f"shared weeks (7)\nmedian {meds[0]:.1f} nats", f"own-role units (17)\nmedian {meds[1]:.1f} nats"])
    ax.set_ylabel(r"ownership price $\lambda_\mathrm{own}$ (nats)")
    ax.set_ylim(0, 22.5); ax.set_xlim(-1, len(rows) + 1)
    ax.set_title(r"(g) ownership acts as a price (Mann–Whitney $p=0.0007$)", loc="left")

    # (h) decomposition of I(agent; repo)
    ax = fig.add_subplot(gs[1, 4])
    allr = sh + ow
    xs = np.r_[np.arange(len(sh)), len(sh) + 1 + np.arange(len(ow))]
    own = np.array([r["own"] for r in allr]); room = np.array([r["room"] for r in allr])
    rs = np.array([max(r["res"], 0.0) for r in allr])
    flo = np.clip(1 - own - room - rs, 0, None)
    ax.bar(xs, own, color=vs.C["orange"], width=0.8, label="ownership")
    ax.bar(xs, room, bottom=own, color=vs.C["green"], width=0.8, label="rooms")
    ax.bar(xs, flo, bottom=own + room, color=vs.NULL, width=0.8, label="run-persistence floor")
    ax.bar(xs, rs, bottom=own + room + flo, color=vs.C["pink"], width=0.8, label="residual (beyond max-ent)")
    ax.axhline(1, color=vs.INK2, lw=0.5)
    ax.set_xticks(xs, ["#" + r["unit"] if not r["unit"].startswith("51") else r["unit"] for r in allr],
                  rotation=90, fontsize=5)
    ax.set_xlim(-1, len(rows) + 1); ax.set_ylim(0, 1.32)
    ax.set_yticks([0, 0.5, 1])
    ax.set_ylabel(r"share of $I(\mathrm{agent};\mathrm{repo})$")
    ax.legend(loc="upper left", fontsize=5.5, ncol=4, bbox_to_anchor=(0.0, 1.02), handlelength=1.0, columnspacing=0.7,
              handletextpad=0.3)
    ax.set_title("(h) where the allocation information goes", loc="left")
    vs.save(fig, HERE / "fig")
    plt.close(fig)
    lam_sh = [r["lam"] for r in sh]; lam_ow = [r["lam"] for r in ow]
    print("median lam shared", np.median(lam_sh), "own", np.median(lam_ow),
          "resid<=0.13 in", sum(r["res"] <= 0.13 for r in rows), "/", len(rows))


if __name__ == "__main__":
    main()
