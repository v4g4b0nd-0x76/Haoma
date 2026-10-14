"""Map creature art for tools/genmaps.py.

Prior gold-wireframe / volumetric-gold bestiary wiped (2026-10).
New 2D beasts are designed one-by-one under static/.preview-maps/beast-review/
and only land here after user approval. Until then CREATURE_ART is empty.
"""
from __future__ import annotations

# Kept so genmaps.art(kind) call sites do not break if a MAPS entry is restored early.
INK = "#080604"


def art(kind, gold=None):
    """Return SVG fragment for kind, or empty string if not yet approved."""
    return CREATURE_ART.get(kind, "")


CREATURE_ART: dict[str, str] = {}
