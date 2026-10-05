"""Group the thesis slides (writeup/slides/theses/H*.tex) by theme, sorted by EU, with a divider slide per theme.

Usage: python3 writeup/slides/make_theme_appendix.py  -> writeup/slides/tables/theses_by_theme.tex
"""
import re
from pathlib import Path

D = Path("writeup/slides/theses")
THEMES = [
    ("How agents couple: reading at the next call", ["H08", "H50", "H40", "H18", "H41", "H02"]),
    ("Subcritical swarms, fields and scaling", ["H67", "H111", "H34", "H51", "H38", "H85", "H36"]),
    ("Goals as fields: quench, remanence, memory", ["H54", "H97", "H96", "H82", "H103", "H88"]),
    ("Rooms as magnetic domains", ["H05", "H100", "H102", "H47", "H108"]),
    ("The context window carries the value", ["H44", "H15", "H69", "H87", "H16", "H71"]),
    ("Identity: style and family fields", ["H46", "H13"]),
    ("Collective order: herding, allocation, culture", ["H11", "H94", "H81", "H89", "H35"]),
]


def meta(h):
    s = (D / f"{h}.tex").read_text()
    claim = re.search(r"\\thesis\{" + h + r"\}\{(.*?)\}\n", s).group(1)
    eu = float(re.findall(r"\{([0-9.]+)\}\{([0-9.]+)\}\s*$", s.strip())[-1][1])
    return claim, eu


have = {p.stem for p in D.glob("H*.tex")}
listed = {h for _, hs in THEMES for h in hs}
extra = sorted(have - listed)
if extra:
    THEMES.append(("Other", extra))
out, n = [], 0
for theme, hs in THEMES:
    hs = [h for h in hs if h in have]
    if not hs:
        continue
    rows = sorted(((h, *meta(h)) for h in hs), key=lambda r: -r[2])
    lst = "\\\\[0.25em]\n".join(f"\\chip{{ink}}{{{h}}}\\ {c} {{\\color{{muted}}(EU {e:.2f})}}" for h, c, e in rows)
    out.append(f"\\begin{{frame}}\n\\vfill{{\\Large\\bfseries {theme}}}\\par\\vspace{{0.8em}}\n{{\\small\n{lst}}}\n\\vfill\n\\end{{frame}}\n")
    out += [f"\\input{{theses/{h}}}\n" for h, _, _ in rows]
    n += len(rows)
Path("writeup/slides/tables/theses_by_theme.tex").write_text("".join(out))
print(n, "thesis slides in", len([t for t in THEMES]), "themes; missing:", sorted(listed - have))
