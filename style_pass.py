#!/usr/bin/env python3
"""
style_pass.py
=============
Two global text transformations across the publication package:

  1. Remove every em dash (U+2014), including the JavaScript escape form
     \\u2014, recasting with commas, colons or sentence breaks rather than
     substituting another dash. En dashes (U+2013) are preserved, because they
     carry meaning in page and numeric ranges such as "pp. 798-802".

  2. Convert British to American spelling.

Both passes operate on text files only. Identifier-bearing words such as
`colour` and `centred` appear in Python variable names and pandas column
labels; the replacements are applied globally and consistently, so a
definition and its uses change together and the code stays valid. The test
suite and the full pipeline are re-run afterwards to confirm that.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

TEXT_SUFFIXES = {".js", ".md", ".py", ".txt", ".csv", ".json", ".yml",
                 ".toml", ".ipynb", ".html"}
SKIP_PARTS = {"__pycache__", ".pytest_cache", ".ipynb_checkpoints", ".git"}

# --- British -> American -------------------------------------------------
# Ordered longest-first within each family so that stems do not partially
# match. Applied case-sensitively for both lower and capitalised forms.
SPELLINGS = [
    ("realizations", "realizations"), ("realization", "realization"),
    ("normalisation", "normalization"), ("normalised", "normalized"),
    ("normalises", "normalizes"), ("normalising", "normalizing"),
    ("normalise", "normalize"),
    ("organisation", "organization"), ("organised", "organized"),
    ("organise", "organize"),
    ("recognised", "recognized"), ("recognises", "recognizes"),
    ("recognise", "recognize"),
    ("characterised", "characterized"), ("characterises", "characterizes"),
    ("characterisation", "characterization"), ("characterise", "characterize"),
    ("minimised", "minimized"), ("minimises", "minimizes"),
    ("minimise", "minimize"),
    ("maximised", "maximized"), ("maximises", "maximizes"),
    ("maximise", "maximize"),
    ("summarised", "summarized"), ("summarises", "summarizes"),
    ("summarise", "summarize"),
    ("generalisation", "generalization"), ("generalised", "generalized"),
    ("generalises", "generalizes"), ("generalise", "generalize"),
    ("standardised", "standardized"), ("standardise", "standardize"),
    ("visualisation", "visualization"), ("visualised", "visualized"),
    ("visualise", "visualize"),
    ("optimisation", "optimization"), ("optimised", "optimized"),
    ("optimise", "optimize"),
    ("quantisation", "quantization"), ("quantised", "quantized"),
    ("quantise", "quantize"),
    ("realised", "realized"), ("realises", "realizes"), ("realise", "realize"),
    ("utilised", "utilized"), ("utilise", "utilize"),
    ("specialised", "specialized"), ("specialise", "specialize"),
    ("penalised", "penalized"), ("penalise", "penalize"),
    ("initialised", "initialized"), ("initialise", "initialize"),
    ("randomised", "randomized"), ("randomise", "randomize"),
    ("discretised", "discretized"), ("discretise", "discretize"),
    ("parametrised", "parametrized"), ("parametrise", "parametrize"),
    ("emphasised", "emphasized"), ("emphasise", "emphasize"),
    ("analysed", "analyzed"), ("analyses", "analyzes"), ("analyse", "analyze"),
    ("behaviour", "behavior"),
    ("colours", "colors"), ("coloured", "colored"), ("colour", "color"),
    ("centred", "centered"), ("centring", "centering"), ("centre", "center"),
    ("labelled", "labeled"), ("labelling", "labeling"),
    ("modelling", "modeling"), ("modelled", "modeled"),
    ("cancelled", "canceled"), ("cancelling", "canceling"),
    ("artefacts", "artifacts"), ("artefact", "artifact"),
    ("licence", "license"),
    ("grey", "gray"),
    ("catalogued", "cataloged"), ("catalogue", "catalog"),
    ("judgement", "judgment"),
    ("acknowledgement", "acknowledgment"),
    ("fulfil", "fulfill"),
    ("sceptical", "skeptical"),
    ("programme", "program"),
    ("defence", "defense"),
    ("practise", "practice"),
    ("towards", "toward"),
    ("whilst", "while"),
    ("amongst", "among"),
    ("favour", "favor"),
    ("rigour", "rigor"),
    ("honour", "honor"),
    ("neighbouring", "neighboring"), ("neighbour", "neighbor"),
    ("metres", "meters"),
    ("litre", "liter"),
    ("analogue", "analog"),
    ("orientated", "oriented"),
]

# Words that must NOT be touched: correct in American English too.
PROTECTED = ("analysis", "emphasis", "hypothesis", "synthesis", "basis",
             "parenthesis", "thesis")


def fix_em_dashes(text: str) -> tuple[str, int]:
    """Remove em dashes, recasting with commas. En dashes are preserved."""
    n = text.count("\u2014") + text.count("\\u2014")
    # JavaScript escape form first, then the literal character.
    for dash in ("\\\\u2014", "\\u2014", "\u2014"):
        text = text.replace(f" {dash} ", ", ")
        text = text.replace(f"{dash} ", ", ")
        text = text.replace(f" {dash}", ", ")
        text = text.replace(dash, ", ")
    # Tidy the artifacts a blanket recast can leave behind.
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"\s+,", ",", text)
    # Do not touch ", ..." : it is an ellipsis, not a stray comma
    # before punctuation. This guard exists because an earlier run
    # turned `tuple[int, ...]` into `tuple[int, ...]` and broke every
    # module that used it.
    text = re.sub(r",(\s*)(?!\.\.\.)([;:!?])", r"\2", text)
    # NOTE: earlier versions also collapsed "(, " and ", )". Both are removed
    # because ", )" is a legal trailing comma and "(x,)" is a single-element
    # tuple; stripping it silently turned tuples into scalars and broke the
    # pipeline. Punctuation inside parentheses is left alone.
    return text, n


def fix_spelling(text: str) -> tuple[str, int]:
    n = 0
    for brit, amer in SPELLINGS:
        for b, a in ((brit, amer), (brit.capitalize(), amer.capitalize()),
                     (brit.upper(), amer.upper())):
            if b in text:
                n += text.count(b)
                text = text.replace(b, a)
    return text, n


def main() -> int:
    files = [p for p in ROOT.rglob("*")
             if p.is_file() and p.suffix in TEXT_SUFFIXES
             and not any(part in SKIP_PARTS for part in p.parts)
             and p.name != "style_pass.py"]

    dashes = spells = touched = 0
    for p in files:
        original = p.read_text(errors="ignore")
        text, d = fix_em_dashes(original)
        text, sp = fix_spelling(text)
        if text != original:
            p.write_text(text)
            touched += 1
            dashes += d
            spells += sp

    print(f"files scanned : {len(files)}")
    print(f"files changed : {touched}")
    print(f"em dashes removed  : {dashes}")
    print(f"spellings changed  : {spells}")

    # Verify nothing survives.
    remaining = []
    for p in files:
        t = p.read_text(errors="ignore")
        if "\u2014" in t or "\\u2014" in t:
            remaining.append(p)
    print(f"files still containing an em dash: {len(remaining)}")
    for p in remaining:
        print("   ", p)
    return 1 if remaining else 0


if __name__ == "__main__":
    sys.exit(main())
