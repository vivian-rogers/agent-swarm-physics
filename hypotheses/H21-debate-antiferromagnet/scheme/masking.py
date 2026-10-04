"""Role/name masking for H21 content vectors.

Debaters must identify themselves at the start of every speech ("As Leader of the Opposition ...") and address
each other by name, so raw embeddings separate the teams by vocabulary alone. Before embedding we replace
(i) agent names and aliases and (ii) team/role words with neutral tokens. Stance words ("support", "oppose",
"the motion") are kept: they are part of the content; the cross-debate 'generic' axis separates them out.

Masked text is never written to disk; only its embeddings are.
"""
from __future__ import annotations

import re

NAME_TOKEN = "someone"
ROLE_TOKEN = "speaker"


STOP_PARTS = {"Claude", "Leader", "Fine-tuned", "Fine-Tuned", "[Temporary]", "Flash", "Code)", "(Claude", "Spark",
              "Muse", "Astra", "Terra", "Luna", "Fable"}


def name_aliases(names):
    """Aliases for agent display names (longest first), e.g. 'Claude Opus 4.1' -> 'Opus 4.1', 'Opus'.

    Pass only the agents on the roster during the period analysed (generic words are never aliases)."""
    al = set()
    for n in names:
        al.add(n)
        parts = n.split()
        if n.startswith("Claude "):
            al.add(n[len("Claude "):])
        if n.endswith(" Pro"):
            al.add(n[: -len(" Pro")])
        for p in parts:
            if len(p) >= 4 and not re.fullmatch(r"[\d.]+", p) and p not in STOP_PARTS:
                al.add(p)  # Sonnet, Opus, Gemini, Grok, GPT-5 ...
        if re.match(r"Claude [\d.]+ \w+", n):  # 'Claude 3.7 Sonnet' -> 'Sonnet 3.7', 'Claude 3.7'
            v, fam = parts[1], parts[2]
            al.update({f"{fam} {v}", f"Claude {v}", f"{v} {fam}"})
    al.add("Claude")
    return sorted(al, key=len, reverse=True)


ROLE_LONG = [
    r"Deputy Prime Minister", r"Prime Minister", r"Deputy Leader of (?:the )?Opposition", r"Leader of (?:the )?Opposition",
    r"Government Whip", r"Opposition Whip", r"Member of (?:the )?(?:Government|Opposition)", r"Government", r"Opposition",
    r"Proposition", r"Opposing team", r"Whip",
]
ROLE_SHORT = [r"Gov", r"Opp", r"PM", r"DPM", r"LO", r"DLO", r"LOO", r"MG", r"MO", r"GW", r"OW"]


def build_masker(names, extra_words=()):
    al = name_aliases(names)
    name_re = re.compile(r"(?<![\w.])@?(?:" + "|".join(re.escape(a) for a in al) + r")(?![\w]|\.\d)", re.IGNORECASE)
    long_re = re.compile(r"\b(?:" + "|".join(ROLE_LONG + [re.escape(w) for w in extra_words]) + r")(?:'s|s)?\b",
                         re.IGNORECASE)
    short_re = re.compile(r"\b(?:" + "|".join(ROLE_SHORT) + r")(?:'s|s)?\b")  # case-sensitive acronyms

    def mask(text: str) -> str:
        t = name_re.sub(NAME_TOKEN, text or "")
        t = long_re.sub(ROLE_TOKEN, t)
        t = short_re.sub(ROLE_TOKEN, t)
        return t

    return mask
