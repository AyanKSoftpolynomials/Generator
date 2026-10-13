"""Arrow helpers."""

import numpy as np
from manim import DOWN, Arrow, CurvedArrow, Mobject, VGroup

from src.components.text import create_label
from src.themes import default_theme as theme


def create_arrow(start: np.ndarray, end: np.ndarray, color: str = theme.ARROW) -> Arrow:
    """Straight arrow between two points (e.g. ``LEFT * 3`` to ``RIGHT * 3``)."""
    return Arrow(start, end, color=color, buff=0, stroke_width=theme.STROKE_NORMAL)


def create_curved_arrow(start: np.ndarray, end: np.ndarray, color: str = theme.ARROW, angle: float = -np.pi / 3) -> CurvedArrow:
    """Arc-shaped arrow, handy for "jumps" on a number line.

    Negative ``angle`` bends it upwards when going left-to-right.
    """
    return CurvedArrow(start, end, angle=angle, color=color, stroke_width=theme.STROKE_NORMAL)


def create_pointer(target: Mobject, label: str | None = None, direction: np.ndarray = DOWN, color: str = theme.ARROW) -> VGroup:
    """Short arrow pointing at ``target`` from ``direction``, with optional label.

    ``direction=DOWN`` puts the arrow above the target pointing down at it.
    """
    tip = target.get_edge_center(-direction) - direction * theme.SPACING_SMALL
    tail = tip - direction * 1.0
    arrow = create_arrow(tail, tip, color=color)
    group = VGroup(arrow)
    if label is not None:
        group.add(create_label(label, color=color).next_to(arrow, -direction, buff=theme.SPACING_SMALL))
    return group
