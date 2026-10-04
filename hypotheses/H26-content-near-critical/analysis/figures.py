"""H26 figures (static PDFs for RevTeX pages).

  synthetic  figures/synthetic_validation.pdf  (H01's P9 under drives; L3 vs realized truth; channel noise)
  real       figures/summary_obs.pdf (per-unit content vs activity vs talk, L3, day and w30)
             figures/ladder.pdf (median gain down the field-removal ladder, per channel and resolution)
             goalperiod-subhypotheses/G<NN>/figures/G<NN>_ladder.pdf
Palette: reference categorical slots 1-3 (validated all-pairs): content blue, activity orange, talk aqua.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
HYP = HERE.parent
ROOT = HYP.parents[1]
D = ROOT / "data/processed/H26-content-near-critical"
FIG = HYP / "figures"
COL = {"c": "#2a78d6", "a": "#eb6834", "k": "#1baf7a"}
NAME = {"c": "content", "a": "activity", "k": "talk"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"

plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "legend.frameon": False,
                     "pdf.fonttype": 42})


def clipg(x, lo=-1.0):
    x = np.asarray(x, float)
    return np.where(np.isfinite(x), np.clip(x, lo, 1), np.nan)


def synthetic():
    R = json.loads((D / "synthetic/synthetic_rows.json").read_text())["two_room"]
    names = list(R.keys())
    short = {"S0_null": "S0", "S1_global": "S1", "S2_global+room": "S2", "S3_global+room_stable": "S3",
             "S4_global+kick+tod+exo": "S4", "S5_J0.2": "S5\n.2", "S5_J0.4": "S5\n.4", "S5_J0.6": "S5\n.6",
             "S6_J0.4+room": "S6\n.4", "S7_J0.4_content_only": "S7\n.4"}
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1.15, 1]})
    # (a) H01 P9 under drives only vs with coupling
    x = np.arange(len(names))
    for i, n in enumerate(names):
        v = np.array([r["est"]["h01_bJ_over_n"] for r in R[n] if r["est"]["h01_bJ_over_n"] is not None], float)
        q = np.percentile(v, [25, 50, 75])
        c = INK2 if "J0" not in n else COL["c"]
        ax[0].plot([i, i], [q[0], q[2]], color=c, lw=2, solid_capstyle="round")
        ax[0].plot(i, q[1], "o", ms=5, color=c, mec="white", mew=0.8)
    ax[0].axhline(0.74, color=INK, lw=0.8, ls="--")
    ax[0].text(-0.4, 0.765, "H01 real median 0.74", ha="left", va="bottom", fontsize=7, color=INK)
    ax[0].axvspan(4.5, len(names) - 0.5, color="#f1f0ec", zorder=0)
    ax[0].text(2, 0.08, "J = 0 (drives only)", ha="center", fontsize=7, color=INK2)
    ax[0].text(7, 0.08, "J > 0", ha="center", fontsize=7, color=INK2)
    ax[0].set_xticks(x); ax[0].set_xticklabels([short[n] for n in names], fontsize=6.5)
    ax[0].set_ylabel(r"H01 P9 estimate $\beta J_0/n$"); ax[0].set_ylim(-0.1, 1.05)
    ax[0].set_title("(a) H01's estimator reads drives as coupling", fontsize=8, loc="left")
    # (b) L3 content and activity vs realized 5-day truth
    for ch, mk in (("c", "o"), ("a", "s")):
        for res, off in (("day", -0.15), ("w30", 0.15)):
            for i, n in enumerate(names):
                e = clipg([r["est"][f"{ch}_{res}_L2"]["g_ex"] for r in R[n]])
                t = np.array([r["truth_realized"][f"{ch}_{res}"]["g_room"] for r in R[n]], float)
                err = e - clipg(t)
                q = np.nanpercentile(err, [25, 50, 75])
                xx = i + off + (0.0 if ch == "c" else 0.07)
                ax[1].plot([xx, xx], [q[0], q[2]], color=COL[ch], lw=1.4, alpha=0.9 if res == "day" else 0.55)
                ax[1].plot(xx, q[1], mk, ms=3.5, color=COL[ch], mec="white", mew=0.5,
                           alpha=1 if res == "day" else 0.6)
    ax[1].axhline(0, color=INK, lw=0.8)
    ax[1].set_xticks(x); ax[1].set_xticklabels([short[n] for n in names], fontsize=6.5)
    ax[1].set_ylabel(r"L3 $g_{ex}$ $-$ realized gain"); ax[1].set_ylim(-1.0, 0.8)
    ax[1].set_title("(b) L3 error (median, IQR; left day, right w30)", fontsize=8, loc="left")
    ax[1].plot([], [], "o", color=COL["c"], label="content"); ax[1].plot([], [], "s", color=COL["a"], label="activity")
    ax[1].legend(loc="lower left", fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_validation.pdf"); plt.close(fig)


def load_units():
    out = {}
    for f in sorted(D.glob("G*/*.json")):
        r = json.loads(f.read_text())
        out[r["unit"]] = r
    return out


TWO = ["35", "36b", "37", "38a", "38b", "38c", "39", "41", "42", "44", "51c"]      # is_two_room() in explore.py
REG3_TWO = [u for u in TWO if u != "35"]
SINGLE = ["40", "51a", "51b", "51d", "51e"]


def val(r, key, lv, stat):
    v = r.get(key, {}).get(lv, {})
    return v.get(stat) if v else None


def real():
    U = load_units()
    SU = {r["unit"]: r for r in json.loads((D / "summary_units.json").read_text())}
    order = [u for u in TWO + SINGLE if u in U]
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7), sharey=True)
    for j, res in enumerate(("day", "w30")):
        a = ax[j]
        for i, u in enumerate(order):
            r = U[u]
            two = u in TWO
            stat = "g_ex" if two else "g_room"
            lv = "L2"
            for ch, off in (("c", -0.22), ("a", 0.0), ("k", 0.22)):
                g = SU[u].get(f"{ch}_{res}_g")
                ci = SU[u].get(f"{ch}_{res}_g_ci")
                if g is None:
                    continue
                g = float(np.clip(g, -1, 1))
                if ci and ci[0] is not None and np.isfinite(ci[0]):
                    lo, hi = np.clip(ci, -1, 1)
                    a.plot([i + off, i + off], [lo, hi], color=COL[ch], lw=1.0, alpha=0.6)
                a.plot(i + off, g, "o" if two else "D", ms=3.8, color=COL[ch], mec="white", mew=0.5)
        a.axhline(0.5, color=INK, lw=0.7, ls="--")
        a.axhline(0, color=INK2, lw=0.6)
        a.axvline(len([u for u in order if u in TWO]) - 0.5, color=INK2, lw=0.6, ls=":")
        a.set_xticks(range(len(order))); a.set_xticklabels(["#" + u for u in order], rotation=90, fontsize=6.5)
        a.set_ylim(-1.0, 1.0)
        a.set_title(f"({'ab'[j]}) {'day means' if res == 'day' else '30-min windows'}", fontsize=8, loc="left")
        ntwo = len([u for u in order if u in TWO])
        a.text(ntwo / 2 - 0.5, -0.93, "two rooms: L3 room excess", ha="center", fontsize=6.5, color=INK2)
        a.text(ntwo + (len(order) - ntwo) / 2 - 0.5, -0.93, "one room: L2", ha="center", fontsize=6.5, color=INK2)
    ax[0].set_ylabel("loop gain g = 1 - 1/VR (clipped at -1)")
    for ch in ("c", "a", "k"):
        ax[0].plot([], [], "o", color=COL[ch], label=NAME[ch])
    fig.legend(loc="upper center", ncol=3, fontsize=7, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(FIG / "summary_obs.pdf"); plt.close(fig)

    # ladder: medians over two-room units
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.3), sharey=True)
    for j, res in enumerate(("day", "w30")):
        a = ax[j]
        steps = [("H01 P9", None), ("L0 all", ("L0", "g_all")), ("L0 room", ("L0", "g_room")),
                 ("L2 room", ("L2", "g_room")), ("L3 excess", ("L2", "g_ex"))]
        lasts = {}
        for ch in ("c", "a", "k"):
            key = f"c_{res}_dedup" if ch == "c" else f"{ch}_{res}"
            ys = []
            for name, spec in steps:
                if spec is None:
                    v = [U[u]["h01_p9"]["raw"]["bJ_over_n"] for u in REG3_TWO if u in U and U[u]["h01_p9"]["raw"]] if ch == "c" and res == "day" else []
                elif spec == ("L2", "g_ex"):
                    v = [SU[u].get(f"{ch}_{res}_g") for u in REG3_TWO]
                else:
                    v = [val(U[u], key, spec[0], spec[1]) for u in REG3_TWO if u in U]
                v = [float(np.clip(x, -1, 1)) for x in v if x is not None and (np.isfinite(x) or x == -np.inf)]
                ys.append(np.median(v) if v else np.nan)
            a.plot(range(len(steps)), ys, "-o", color=COL[ch], lw=2, ms=4, label=NAME[ch])
            lasts[ch] = ys[-1]
        placed = []
        for ch, last in sorted(lasts.items(), key=lambda kv: kv[1]):
            if not np.isfinite(last):
                continue
            y = last
            while any(abs(y - p) < 0.05 for p in placed):
                y += 0.05
            placed.append(y)
            a.text(len(steps) - 0.88, y, f"{last:.2f}", color=COL[ch], fontsize=7, va="center")
        a.set_xticks(range(len(steps))); a.set_xticklabels([s for s, _ in steps], fontsize=7)
        a.axhline(0.5, color=INK, lw=0.7, ls="--")
        a.set_xlim(-0.3, len(steps) - 0.2)
        a.set_title(f"({'ab'[j]}) {'day means' if res == 'day' else '30-min windows'}: median, 10 regime-III two-room units",
                    fontsize=7.5, loc="left")
    ax[0].set_ylabel("median loop gain")
    ax[0].legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIG / "ladder.pdf"); plt.close(fig)

    # per-period ladders
    by_goal = {}
    for u, r in U.items():
        by_goal.setdefault(r["goal_no"], []).append(u)
    for g, us in by_goal.items():
        us = sorted(us)
        fig, axs = plt.subplots(1, len(us), figsize=(2.2 * len(us) + 0.4, 2.2), squeeze=False, sharey=True)
        for a, u in zip(axs[0], us):
            r = U[u]
            two = u in TWO
            for ch in ("c", "a", "k"):
                for res, ls in (("day", "-"), ("w30", "--")):
                    key = f"c_{res}_dedup" if ch == "c" else f"{ch}_{res}"
                    seq = [val(r, key, "L0", "g_room"), val(r, key, "L2", "g_room")] + ([val(r, key, "L2", "g_ex")] if two else [])
                    seq = [np.clip(x, -1, 1) if x is not None else np.nan for x in seq]
                    a.plot(range(len(seq)), seq, ls, marker="o", ms=3, color=COL[ch], lw=1.4,
                           label=f"{NAME[ch]} {res}" if u == us[0] else None)
            a.set_xticks(range(3 if two else 2)); a.set_xticklabels(["L0 room", "L2 room", "L3 excess"][: 3 if two else 2], fontsize=6.5)
            a.axhline(0.5, color=INK, lw=0.6, ls=":"); a.axhline(0, color=INK2, lw=0.5)
            a.set_ylim(-1, 1); a.set_title(f"#{u}", fontsize=8)
        axs[0][0].set_ylabel("loop gain")
        axs[0][0].legend(fontsize=5.5, loc="lower left", ncol=1)
        fig.tight_layout()
        out = HYP / "goalperiod-subhypotheses" / f"G{g:02d}" / "figures"
        out.mkdir(parents=True, exist_ok=True)
        fig.savefig(out / f"G{g:02d}_ladder.pdf"); plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    if "synthetic" in sys.argv or len(sys.argv) == 1:
        synthetic()
    if "real" in sys.argv or len(sys.argv) == 1:
        real()


def summary_page():
    """figures/summary.pdf: one letter page stacking ladder, per-unit and synthetic figures with a caption."""
    from pypdf import PdfReader, PdfWriter, Transformation, PageObject
    W, H = 612, 792
    page = PageObject.create_blank_page(width=W, height=H)
    y = H - 40
    for name in ("ladder", "summary_obs", "synthetic_validation"):
        src = PdfReader(str(FIG / f"{name}.pdf")).pages[0]
        w, h = float(src.mediabox.width), float(src.mediabox.height)
        s = (W - 60) / w
        y -= h * s + 12
        page.merge_transformed_page(src, Transformation().scale(s).translate(30, y))
    # caption via a small matplotlib pdf
    fig = plt.figure(figsize=(W / 72, 0.9))
    fig.text(0.05, 0.85, "H26 round 1 (2026-10-04). Top: median loop gain g = 1 - 1/VR down the field-removal ladder for content, activity, talk "
             "(10 regime-III two-room units).", fontsize=7, va="top")
    fig.text(0.05, 0.55, "Middle: per-unit drive-removed gains, joint day-bootstrap 95% CIs (diamonds: one-room units, L2 upper bounds). "
             "Bottom: synthetic validation.", fontsize=7, va="top")
    fig.text(0.05, 0.25, "Reading: content's room excess (~0.5) is real but activity's is as large at matched resolution; H01's 0.74 is "
             "reproduced by drives alone (S1-S4).", fontsize=7, va="top")
    cap = FIG / "_caption_tmp.pdf"
    fig.savefig(cap); plt.close(fig)
    cp = PdfReader(str(cap)).pages[0]
    page.merge_transformed_page(cp, Transformation().translate(0, 20))
    wr = PdfWriter(); wr.add_page(page)
    with open(FIG / "summary.pdf", "wb") as fh:
        wr.write(fh)
    cap.unlink()


if __name__ == "__main__" and "page" in sys.argv:
    summary_page()


def column_figs():
    """Column-width (3.4 in) versions for the RevTeX summary page."""
    U = load_units()
    SU = {r["unit"]: r for r in json.loads((D / "summary_units.json").read_text())}
    with plt.rc_context({"font.size": 6.5}):
        fig, ax = plt.subplots(1, 2, figsize=(3.45, 1.75), sharey=True)
        steps = [("H01\nP9", None), ("L0\nall", ("L0", "g_all")), ("L0\nroom", ("L0", "g_room")),
                 ("L2\nroom", ("L2", "g_room")), ("L3\nexcess", ("L2", "g_ex"))]
        for j, res in enumerate(("day", "w30")):
            a = ax[j]
            for ch in ("c", "a", "k"):
                key = f"c_{res}_dedup" if ch == "c" else f"{ch}_{res}"
                ys = []
                for name, spec in steps:
                    if spec is None:
                        v = [U[u]["h01_p9"]["raw"]["bJ_over_n"] for u in REG3_TWO if U[u]["h01_p9"]["raw"]] if ch == "c" and res == "day" else []
                    elif spec == ("L2", "g_ex"):
                        v = [SU[u].get(f"{ch}_{res}_g") for u in REG3_TWO]
                    else:
                        v = [val(U[u], key, spec[0], spec[1]) for u in REG3_TWO]
                    v = [float(np.clip(x, -1, 1)) for x in v if x is not None and (np.isfinite(x) or x == -np.inf)]
                    ys.append(np.median(v) if v else np.nan)
                a.plot(range(len(steps)), ys, "-o", color=COL[ch], lw=1.5, ms=2.8, label=NAME[ch])
            a.axhline(0.5, color=INK, lw=0.6, ls="--")
            a.set_xticks(range(len(steps))); a.set_xticklabels([s for s, _ in steps], fontsize=5.5)
            a.set_title("day means" if res == "day" else "30-min windows", fontsize=6.5, loc="left")
            a.set_ylim(0.25, 0.95)
        ax[0].set_ylabel("median loop gain")
        ax[1].legend(fontsize=5.5, loc="lower left", handlelength=1.2)
        fig.tight_layout(pad=0.3)
        fig.savefig(FIG / "summary_obs_col.pdf"); plt.close(fig)

        R = json.loads((D / "synthetic/synthetic_rows.json").read_text())["two_room"]
        names = list(R.keys())
        short = ["null", "global", "+room", "+room\nstable", "+kick\nTOD exo", ".2", ".4", ".6", ".4\n+room", ".4\ncont."]
        fig, a = plt.subplots(1, 1, figsize=(3.45, 1.85))
        for i, n in enumerate(names):
            v = np.array([r["est"]["h01_bJ_over_n"] for r in R[n] if r["est"]["h01_bJ_over_n"] is not None], float)
            q = np.percentile(v, [25, 50, 75])
            c = INK2 if "J0" not in n else COL["c"]
            a.plot([i, i], [q[0], q[2]], color=c, lw=2)
            a.plot(i, q[1], "o", ms=3.5, color=c, mec="white", mew=0.5)
            e = np.clip([r["est"]["c_day_L2"]["g_ex"] for r in R[n]], -1, 1)
            a.plot(i + 0.28, np.nanmedian(e), "s", ms=3, color=COL["k"], mec="white", mew=0.4)
            t = np.median([r["truth_realized"]["c_day"]["g_room"] for r in R[n]])
            a.plot(i + 0.28, t, "_", ms=7, color=INK, mew=1.0)
        a.axhline(0.74, color=INK, lw=0.6, ls="--")
        a.text(-0.4, 0.765, "H01 real 0.74", fontsize=5.5, color=INK)
        a.axvspan(4.5, len(names) - 0.5, color="#f1f0ec", zorder=0)
        a.text(2, -0.08, "J = 0 (drives only)", ha="center", fontsize=5.5, color=INK2)
        a.text(7, -0.08, "coupling J > 0", ha="center", fontsize=5.5, color=INK2)
        a.set_xticks(range(len(names))); a.set_xticklabels(short, fontsize=5)
        a.set_ylim(-0.15, 1.13); a.set_ylabel("estimate")
        a.plot([], [], "o", color=INK2, ms=3, label="H01 P9 βJ₀/n (median, IQR)")
        a.plot([], [], "s", color=COL["k"], ms=3, label="H26 L3 content g_ex")
        a.plot([], [], "_", color=INK, ms=7, mew=1, label="realized latent gain")
        a.legend(fontsize=5, loc="upper center", ncol=3, handlelength=1.0, columnspacing=0.8, borderaxespad=0.2)
        fig.tight_layout(pad=0.3)
        fig.savefig(FIG / "synthetic_col.pdf"); plt.close(fig)


if __name__ == "__main__" and "col" in sys.argv:
    column_figs()
