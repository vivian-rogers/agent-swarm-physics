"""Build the visuals compendium (RevTeX PDF) and a local HTML gallery from writeup/visuals/H*/.

Usage: uv run python writeup/visuals/build_gallery.py   (then pdflatex compendium.tex twice in writeup/visuals/)
"""
import html, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
THEMES = [
    ("How agents couple: reading at the next call", ["H08", "H50", "H40", "H18", "H41"]),
    ("Subcritical swarms, fields and scaling", ["H67", "H111", "H34", "H51", "H38", "H85"]),
    ("Goals as fields: quench, remanence, memory", ["H54", "H97", "H96", "H82", "H103", "H88"]),
    ("Rooms as magnetic domains", ["H05", "H100", "H102", "H47", "H108"]),
    ("The context window carries the value", ["H44", "H69", "H87", "H16", "H71"]),
    ("Collective order: herding, allocation, culture", ["H11", "H94", "H81", "H89", "H35"]),
]
folders = {p.name.split("-")[0]: p for p in HERE.iterdir() if p.is_dir() and re.match(r"H\d+-", p.name)}
listed = [h for _, hs in THEMES for h in hs]
missing = sorted(set(folders) - set(listed))
if missing:
    THEMES.append(("Other", missing))


def caption_tex(p):
    return (p / "caption.tex").read_text().strip()


def tex_to_html(t):
    t = re.sub(r"\\label\{[^}]*\}", "", t)
    t = t.strip()
    if t.startswith("\\caption{"):
        t = t[len("\\caption{"):]
        t = t[: t.rfind("}")]
    rep = [(r"\%", "%"), ("---", "\u2014"), ("--", "\u2013"), (r"\,", "\u2009"), ("{,}", ","), ("~", "\u00a0"),
           (r"\ldots", "\u2026"), (r"\times", "\u00d7"), (r"\pm", "\u00b1"), (r"\le", "\u2264"), (r"\ge", "\u2265"),
           (r"\approx", "\u2248"), (r"\to", "\u2192"), (r"\rightarrow", "\u2192"), (r"\infty", "\u221e"),
           (r"\chi", "\u03c7"), (r"\rho", "\u03c1"), (r"\kappa", "\u03ba"), (r"\lambda", "\u03bb"), (r"\tau", "\u03c4"),
           (r"\sigma", "\u03c3"), (r"\phi", "\u03c6"), (r"\varphi", "\u03c6"), (r"\Phi", "\u03a6"), (r"\Delta", "\u0394"),
           (r"\gamma", "\u03b3"), (r"\beta", "\u03b2"), (r"\alpha", "\u03b1"), (r"\eta", "\u03b7"), (r"\mu", "\u03bc"),
           (r"\theta", "\u03b8"), (r"\psi", "\u03c8"), (r"\cdot", "\u00b7"), (r"\sim", "\u223c"), (r"\langle", "\u27e8"),
           (r"\rangle", "\u27e9"), (r"\hat", ""), (r"\mathrm", ""), (r"\mathit", ""), (r"\rm", ""), (r"\left", ""), (r"\right", "")]
    t = html.escape(t, quote=False)
    for a, b in rep:
        t = t.replace(a, b)
    t = re.sub(r"\\(?:textbf|emph|textit|textsc|texttt)\{([^{}]*)\}", r"\1", t)
    t = re.sub(r"\\(?:textbf|emph|textit|textsc|texttt)\{([^{}]*)\}", r"\1", t)
    t = re.sub(r"_\{([^{}]*)\}", r"<sub>\1</sub>", t)
    t = re.sub(r"\^\{([^{}]*)\}", r"<sup>\1</sup>", t)
    t = re.sub(r"_([A-Za-z0-9])", r"<sub>\1</sub>", t)
    t = re.sub(r"\^([A-Za-z0-9\u2212-])", r"<sup>\1</sup>", t)
    t = t.replace("$", "").replace("{", "").replace("}", "").replace("\\", "")
    return t


# ---------- RevTeX compendium
tex = [r"""\documentclass[aps,prl,reprint,superscriptaddress,nofootinbib]{revtex4-2}
\usepackage{graphicx}\usepackage{amsmath,amssymb}\usepackage[T1]{fontenc}
\begin{document}
\title{Agent-swarm physics: figure compendium}
\author{Vivian Rogers}\affiliation{with Claude Opus 5.5}
\date{2026-10-04}
\begin{abstract}
Writeup figures for the hypotheses with the clearest results, grouped by theme. Each figure is rebuilt by \texttt{writeup/visuals/H\textit{NN}-*/make.py} from processed, non-holdout data; animations (where they exist) are \texttt{anim.mp4} in the same folder, and the static figure here is the version for print. Numbers in captions come from the hypothesis cards; nothing here is holdout-confirmed. Data: AI Village (AI Digest).
\end{abstract}
\maketitle
"""]
for theme, hs in THEMES:
    tex.append(f"\\section*{{{theme}}}\n")
    for h in hs:
        p = folders.get(h)
        if not p:
            continue
        cap = caption_tex(p)
        anim = " Animation: \\texttt{" + p.name.replace("_", "\\_") + "/anim.mp4}." if (p / "anim.mp4").exists() else ""
        if anim:
            i = cap.rfind("\\label")
            j = cap.rfind("}", 0, i if i > 0 else len(cap))
            cap = cap[:j] + anim + cap[j:]
        tex.append("\\begin{figure*}[p]\n\\centering\n\\includegraphics[width=\\textwidth]{" + p.name + "/fig.pdf}\n" + cap + "\n\\end{figure*}\n")
    tex.append("\\clearpage\n")
tex.append("\\end{document}\n")
(HERE / "compendium.tex").write_text("".join(tex))

# ---------- HTML gallery (local; mp4 paths are relative)
cards = []
toc = []
for ti, (theme, hs) in enumerate(THEMES):
    toc.append(f'<a href="#t{ti}">{html.escape(theme)}</a>')
    items = []
    for h in hs:
        p = folders.get(h)
        if not p:
            continue
        cap = tex_to_html(caption_tex(p))
        parts = re.split(r"\.\s+", cap, maxsplit=1); first, rest = parts[0], (parts[1] if len(parts) > 1 else "")
        media = f'<img loading="lazy" src="{p.name}/fig.png" alt="{html.escape(first)}">'
        vid = ""
        if (p / "anim.mp4").exists():
            vid = (f'<video controls loop muted playsinline preload="none" poster="{p.name}/anim_poster.png">'
                   f'<source src="{p.name}/anim.mp4" type="video/mp4"></video>')
        items.append(f'''<article id="{h}"><header><span class="hid">{h}</span><h3>{html.escape(first)}.</h3>
<span class="badge">{"figure + animation" if vid else "figure"}</span></header>
<div class="media">{vid}{media}</div>
<details><summary>Caption</summary><p>{rest}</p><p class="src">{p.name}/ · make.py rebuilds it</p></details></article>''')
    cards.append(f'<section id="t{ti}"><h2>{html.escape(theme)}</h2>{"".join(items)}</section>')

page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Swarm physics visuals</title>
<style>
:root{{--bg:#fbfbfa;--panel:#ffffff;--ink:#1a1a1a;--ink2:#4d4d4d;--muted:#8c8c8c;--line:#e6e6e6;--acc:#0072B2;--acc2:#E69F00}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#16181b;--panel:#1f2226;--ink:#ececec;--ink2:#c2c2c2;--muted:#8f8f8f;--line:#33373c;--acc:#56B4E9;--acc2:#E69F00}}}}
:root[data-theme="dark"]{{--bg:#16181b;--panel:#1f2226;--ink:#ececec;--ink2:#c2c2c2;--muted:#8f8f8f;--line:#33373c;--acc:#56B4E9;--acc2:#E69F00}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 "Iowan Old Style","Palatino Linotype",Georgia,serif}}
header.top{{padding:28px 16px 8px;max-width:1180px;margin:0 auto}}
header.top h1{{margin:0 0 4px;font-size:26px}} header.top p{{margin:0;color:var(--ink2)}}
nav{{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);z-index:2}}
nav div{{max-width:1180px;margin:0 auto;padding:8px 16px;display:flex;gap:14px;flex-wrap:wrap;font:13px system-ui,sans-serif}}
nav a{{color:var(--acc);text-decoration:none}}
main{{max-width:1180px;margin:0 auto;padding:0 16px 48px}}
h2{{margin:32px 0 12px;font-size:20px;border-bottom:2px solid var(--acc2);padding-bottom:4px}}
article{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:14px;margin:0 0 18px}}
article header{{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}}
.hid{{font:600 13px system-ui,sans-serif;color:var(--acc)}} h3{{margin:0;font-size:16px;flex:1;min-width:240px}}
.badge{{font:12px system-ui,sans-serif;color:var(--muted)}}
.media{{display:grid;gap:12px;margin-top:10px}} .media img,.media video{{width:100%;height:auto;border-radius:4px;background:#fff}}
details{{margin-top:8px;color:var(--ink2)}} summary{{cursor:pointer;font:13px system-ui,sans-serif;color:var(--acc)}}
.src{{font:12px ui-monospace,monospace;color:var(--muted)}}
</style></head><body>
<header class="top"><h1>Swarm physics: figures and animations</h1>
<p>{sum(1 for _ in folders)} hypotheses · {sum(1 for p in folders.values() if (p/'anim.mp4').exists())} animations · AI Village data (AI Digest), non-holdout only · state 2026-10-04 · local file, not for upload</p></header>
<nav><div>{"".join(toc)}</div></nav>
<main>{"".join(cards)}</main></body></html>"""
(HERE / "index.html").write_text(page)
print(len(folders), "folders;", "missing from themes:", missing)
