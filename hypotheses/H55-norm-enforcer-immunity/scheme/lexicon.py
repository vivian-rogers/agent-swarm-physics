"""H55 correction / norm-enforcement / decline lexicon (v1). FROZEN 2026-10-04 06:27 UTC, before the blind validation
sample was drawn. Applied to message text in memory only; callers store booleans, never text.

Families (case-insensitive):
  corr  points out an error, wrong status, broken link, duplicate, or corrects a detail
  norm  asks someone to change behaviour on a rule / norm / ethics / process ground
  decl  declines or refuses a request
A message counts as a *correction (H55 lexical marker)* when it is ADDRESSED (decided by the caller from structure)
and matches any family.
"""
from __future__ import annotations

import re

_CORR = [
    r"(?:^|[.!?;:\n]\s*|\b(?:but|and|so)\s+)actually\b",
    r"\bcorrection\b", r"\bto clarify\b", r"\bclarification\b",
    r"\bnot (?:quite |entirely |exactly )?(?:right|correct|accurate|true)\b",
    r"\bincorrect(?:ly)?\b", r"\binaccura(?:te|cy)\b", r"\bwrong\b", r"\bmistak(?:e|es|en)\b", r"\btypo\b",
    r"\berror in\b", r"\bmisread\b", r"\bmisunderst(?:ood|and)\b", r"\bthat(?:'|’)?s not\b", r"\bthat is not\b",
    r"\b(?:isn(?:'|’)?t|is not|wasn(?:'|’)?t|was not) (?:right|correct|true|accurate)\b", r"\bshould be\b", r"\byou mean\b", r"\bbroken link\b",
    r"\b404\b", r"\b(?:doesn|does not|don|do not|didn|did not)(?:'|’)?t? (?:work|load|exist|resolve|open)\b",
    r"\balready (?:been )?(?:done|posted|exists?|claimed|covered|taken|submitted|merged|fixed)\b",
    r"\bduplicat(?:e|es|ed|ing)\b", r"\boutdated\b", r"\bno longer\b",
    r"\bnot (?:yet )?(?:live|deployed|published|merged)\b",
]
_NORM = [
    r"\bplease (?:don(?:'|’)?t|do not|stop|avoid|refrain|hold off)\b", r"\blet(?:'|’)?s (?:not|avoid|stop)\b",
    r"\bwe (?:shouldn(?:'|’)?t|should not|agreed|can(?:'|’)?t|cannot)\b", r"\breminder\b",
    r"\bagainst (?:the |our )?(?:rules|guidelines|policy|policies)\b", r"\bnot allowed\b", r"\bviolat(?:e|es|ed|ing|ion)\b",
    r"\bspam(?:ming|my)?\b", r"\bconsent\b", r"\bboundar(?:y|ies)\b", r"\binappropriate\b", r"\bharmful\b",
    r"\bunethical\b", r"\bprivacy\b", r"\boff[- ]topic\b", r"\bstay on (?:topic|task)\b",
    r"\bstop (?:posting|repeating|spamming|sending)\b", r"\brepeating (?:yourself|the same)\b", r"\bloop(?:s|ing)?\b",
]
_DECL = [
    r"\bi (?:can(?:'|’)?t|cannot|won(?:'|’)?t|will not|am unable|(?:'|’)m unable|must decline|decline|(?:'|’)ll pass|"
    r"will pass|(?:'|’)d rather not|am not able|(?:'|’)m not able|(?:'|’)m not comfortable|am not comfortable)\b",
    r"\bcan(?:'|’)?t help with\b", r"\bnot going to\b",
]

RX = {k: re.compile("|".join(v), re.I) for k, v in (("corr", _CORR), ("norm", _NORM), ("decl", _DECL))}
VERSION = "h55-lexicon-v1"


def families(text: str | None) -> dict:
    t = text or ""
    return {k: bool(rx.search(t)) for k, rx in RX.items()}


def any_family(text: str | None) -> bool:
    t = text or ""
    return any(rx.search(t) for rx in RX.values())
