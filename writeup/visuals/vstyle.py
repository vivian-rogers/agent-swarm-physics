"""Shared look for writeup visuals and animations (writeup/visuals/).

Usage:
    import sys; sys.path.insert(0, "writeup/visuals"); import vstyle as vs
    vs.use()                       # rcParams for RevTeX figures
    fig, ax = vs.figure("single")  # 3.4 in wide; "double" = 7.0 in
    vs.save(fig, "writeup/visuals/H08-.../fig")   # writes fig.pdf + fig.png
    vs.save_anim(anim, "writeup/visuals/H08-.../anim", fps=24)  # -> writeup/animations/H08-....mp4 (+ _poster.png)
"""
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt

# Okabe-Ito order (validated: lightness, chroma, normal-vision pass; CVD 7.6 for pink/green,
# so every series also carries a direct label or a marker shape). Never cycle past these.
C = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73", "pink": "#CC79A7",
     "sky": "#56B4E9", "red": "#D55E00"}
CAT = [C["blue"], C["orange"], C["green"], C["pink"], C["sky"], C["red"]]
INK, INK2, MUTED, GRID = "#1a1a1a", "#4d4d4d", "#8c8c8c", "#e6e6e6"
NULL = "#b3b3b3"          # null bands / shuffled controls are always gray
FIELD, COUPLING = C["orange"], C["blue"]   # fixed meaning across the whole set
ROOM = {"#best": C["blue"], "#rest": C["red"], "#general": C["green"], "#focus": C["pink"]}
SEQ = "Blues"; DIV = "RdBu_r"   # sequential one hue; diverging with gray-white midpoint
W = {"single": 3.4, "double": 7.0}

def use():
    mpl.rcParams.update({
        "font.family": "serif", "font.serif": ["STIX Two Text", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix", "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7, "legend.frameon": False,
        "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
        "grid.color": GRID, "grid.linewidth": 0.5, "axes.axisbelow": True,
        "lines.linewidth": 1.5, "lines.markersize": 4, "axes.prop_cycle": mpl.cycler(color=CAT),
        "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
        "pdf.fonttype": 42, "animation.ffmpeg_path": "/opt/homebrew/bin/ffmpeg",
    })

def figure(width="single", aspect=0.68, **kw):
    w = W.get(width, width)
    return plt.subplots(figsize=(w, w * aspect), **kw)

def label_end(ax, x, y, text, color, dx=4, **kw):
    """Direct label at a line's end (identity never by color alone)."""
    ax.annotate(text, (x, y), xytext=(dx, 0), textcoords="offset points", color=INK,
                va="center", fontsize=7, **kw)

def save(fig, stem):
    stem = Path(stem)
    if stem.name == "anim":  # writeup/visuals/<F>/anim -> writeup/animations/<F>
        stem = Path(__file__).resolve().parent.parent / "animations" / stem.resolve().parent.name
    stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf")); fig.savefig(stem.with_suffix(".png"))

def save_anim(anim, stem, fps=24, dpi=160, poster_frame=-1):
    """mp4 (H.264, yuv420p) plus a poster PNG of one frame; the writeup figure is separate (save)."""
    stem = Path(stem)
    if stem.name == "anim":  # writeup/visuals/<F>/anim -> writeup/animations/<F>
        stem = Path(__file__).resolve().parent.parent / "animations" / stem.resolve().parent.name
    stem.parent.mkdir(parents=True, exist_ok=True)
    w = mpl.animation.FFMpegWriter(fps=fps, codec="h264", bitrate=2400,
                                   extra_args=["-pix_fmt", "yuv420p", "-movflags", "+faststart"])
    anim.save(stem.with_suffix(".mp4"), writer=w, dpi=dpi)
    n = anim._save_count if hasattr(anim, "_save_count") else None
    try:
        anim._func(poster_frame if poster_frame >= 0 else (n - 1 if n else 0))
    except Exception:
        pass
    anim._fig.savefig(stem.parent / (stem.name + "_poster.png"))
