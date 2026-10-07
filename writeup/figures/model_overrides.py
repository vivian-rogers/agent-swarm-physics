"""Override layer for the physics-model assignments of each card (2026-10-07).

Physics models 16 (physics-models/16-langevin-relaxation) and 17 (physics-models/17-collective-modes)
were added on 2026-10-07. The `models` field of every hypotheses/H*/summary/meta.json still lists only
models 01-15. This module applies the reassignments from the two model READMEs ("Cards that test it")
and physics-models/README.md ("Status of each model") on top of meta.json, so that every writeup
figure sees 17 model columns. It does not edit meta.json. When the meta.json files carry 16 and 17
themselves, `apply` adds nothing twice (it checks for an existing entry first) and this file can go.

Reassignments (2026-10-07):
  model 17 (collective modes) as primary; the old primary 01 and/or 11 becomes secondary, outcome kept:
    H12 mixed, H91 refuted, H92 mixed
  model 17 as secondary: H81 mixed, H108 mixed, H36 refuted (the spectral alarm)
  model 16 (Langevin relaxation) as primary; the old primary 11 becomes secondary, outcome kept:
    H97 mixed (restoring force supported, literal law fails), H125 mixed (underdamped rejected,
    overdamped supported), H127 refuted, H130 mixed (one-rate kill fired; two-rate kick found)
  model 16 as secondary: H71 mixed, H46 refuted (OU drift kill fired), H81 mixed,
    H106 untested (inconclusive, power 0)
  H72: unchanged (09 primary refuted, 02 secondary supported); the 02 entry is the
    context-held self-field variant (note added).

Usage (from the project root):
    sys.path.insert(0, "writeup/figures"); import model_overrides as mo
    hs = mo.load_hypotheses()        # scored cards (with meta.json), sorted by number, overrides applied
    mo.COLS, mo.SHORT, mo.NAME       # 17 model ids, short and long column labels
"""
import copy
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "dashboard"))
import collect  # noqa: E402

DATE = "2026-10-07"
COLS = [f"{i:02d}" for i in range(1, 18)]
SHORT = ["inv. Ising", "kin. Ising", "contagion", "sem. info", "replicators", "neutral", "fluct. env.", "copying",
         "Hawkes", "Potts", "vector spins", "info dyn.", "conventions", "scaling", "stoch. thermo",
         "Langevin", "coll. modes"]
NAME = {"01": "inverse Ising", "02": "kinetic Ising", "03": "contagion", "04": "semantic info", "05": "replicators",
        "06": "neutral", "07": "fluct. env.", "08": "copying", "09": "Hawkes", "10": "Potts", "11": "vector spins",
        "12": "info dynamics", "13": "conventions", "14": "scaling", "15": "stoch. thermo",
        "16": "Langevin relaxation", "17": "collective modes"}

# (card, model, outcome, note): the new model becomes primary; the card's old primaries become secondary.
NEW_PRIMARY = [
    ("H12", "17", "mixed", "collective modes above a calibrated RMT edge (talk 21/24, content 24/24); activity mode is the scheduler"),
    ("H91", "17", "refuted", "eigenvector rotation alarm AUC 0.56 loses to the centroid alarm 0.96"),
    ("H92", "17", "mixed", "clipping at a calibrated edge beats the raw matrix (26/32) but ties Ledoit-Wolf"),
    ("H97", "16", "mixed", "restoring force supported (overdamped well, day-1 overshoot); the literal linear isotropic law fails"),
    ("H125", "16", "mixed", "underdamped oscillator rejected (no undershoot); overdamped well supported"),
    ("H127", "16", "refuted", "no call-rate-set relaxation: 74% reach the plateau within the read-out call"),
    ("H130", "16", "mixed", "one-rate OU kill K1 fired; a two-rate form (fast read kick on a slow well) found"),
]
# (card, model, outcome, note): added as secondary if the card does not already carry the model.
NEW_SECONDARY = [
    ("H81", "17", "mixed", "slow collective content mode beyond composition, regime I only"),
    ("H108", "17", "mixed", "room content direction persists (supported by rule, fragile)"),
    ("H36", "17", "refuted", "the spectral (susceptibility, multi-information) alarm fails random dates"),
    ("H71", "16", "mixed", "set point yes, first-order relaxation no; a two-timescale homeostat fits"),
    ("H46", "16", "refuted", "OU drift-and-reset of style: kill rule fired (no decay of the offset)"),
    ("H81", "16", "mixed", "one OU collective slow mode, tau about 23-28 days in regime I"),
    ("H106", "16", "untested", "1/N rotational diffusion: inconclusive, power 0 (shown as untested)"),
]
# (card, model, role, note): annotate an existing entry.
NOTES = [
    ("H72", "02", "secondary", "context-held self-field variant of 02 (own-idle-share urn)"),
]
SRC = f"model_overrides {DATE}"


def apply(hid: str, models: list[dict]) -> list[dict]:
    """Return a copy of a card's model list with the 2026-10-07 overrides applied."""
    out = copy.deepcopy(models or [])
    for h, mid, outcome, note in NEW_PRIMARY:
        if h != hid or any(m["model"] == mid for m in out):
            continue
        for m in out:
            if m["role"] == "primary":
                m["role"] = "secondary"
                m["note"] = (m.get("note", "") + f" [primary until {DATE}]").strip()
        out.insert(0, {"model": mid, "role": "primary", "outcome": outcome, "note": note, "source": SRC})
    for h, mid, outcome, note in NEW_SECONDARY:
        if h == hid and not any(m["model"] == mid for m in out):
            out.append({"model": mid, "role": "secondary", "outcome": outcome, "note": note, "source": SRC})
    for h, mid, role, note in NOTES:
        if h == hid:
            for m in out:
                if m["model"] == mid and m["role"] == role and note not in m.get("note", ""):
                    m["note"] = (m.get("note", "") + "; " + note).strip("; ")
    return out


def hnum(name: str) -> int:
    return int(re.match(r"^H(\d+)", name).group(1))


def load_hypotheses(scored_only: bool = True) -> list[dict]:
    """collect.hypothesis() for every card, sorted by number, with overrides applied to `models`.
    scored_only: keep cards that have summary/meta.json (the scored set; pre-registrations without one are left out)."""
    hs = []
    dirs = [d for d in collect.HYP.iterdir() if d.is_dir() and re.match(r"^H\d{2,}-", d.name)]
    for d in sorted(dirs, key=lambda d: hnum(d.name)):
        if scored_only and not (d / "summary/meta.json").exists():
            continue
        h = collect.hypothesis(d)
        h["models"] = apply(h["id"], h.get("models") or [])
        hs.append(h)
    return hs


def clean_title(t: str) -> str:
    """House words for titles in figures: no 'holdout', no 'gate'."""
    t = t.replace("gating", "coupling").replace("gated", "filtered").replace("Gated", "Filtered")
    t = re.sub(r"\bgates?\b", "filter", t)
    return t.replace("Holdout", "Reserved").replace("holdout", "reserved")


if __name__ == "__main__":
    hs = load_hypotheses()
    print(len(hs), "scored cards")
    for h in hs:
        if any(m.get("source") == SRC or DATE in m.get("note", "") or h["id"] == "H72" for m in h["models"]):
            print(h["id"], [(m["model"], m["role"], m["outcome"]) for m in h["models"]])
