"""Emphasis helpers: underlines and correct / incorrect answer indicators.

The tick and cross are drawn with lines (not font glyphs), so they look the
same on every machine.
"""

from manim import DL, DR, UL, UR, Circle, Line, Mobject, Underline, VGroup, VMobject

from src.themes import default_theme as theme


def create_underline(target: Mobject, color: str = theme.HIGHLIGHT) -> Underline:
    """Line under ``target``. Animate it with ``Create`` for a "writing" effect."""
    return Underline(target, color=color, stroke_width=theme.STROKE_NORMAL, buff=theme.SPACING_SMALL / 2)


def create_correct_indicator(radius: float = 0.4) -> VGroup:
    """Green circle with a tick. Place it with ``.next_to(answer, RIGHT)``."""
    circle = Circle(radius=radius, color=theme.CORRECT, stroke_width=theme.STROKE_NORMAL)
    tick = VMobject(color=theme.CORRECT, stroke_width=theme.STROKE_THICK)
    tick.set_points_as_corners([
        [-0.45 * radius, 0.0, 0],
        [-0.1 * radius, -0.35 * radius, 0],
        [0.5 * radius, 0.35 * radius, 0],
    ])
    return VGroup(circle, tick)


def create_incorrect_indicator(radius: float = 0.4) -> VGroup:
    """Red circle with a cross. Place it with ``.next_to(answer, RIGHT)``."""
    circle = Circle(radius=radius, color=theme.INCORRECT, stroke_width=theme.STROKE_NORMAL)
    size = 0.4 * radius
    cross = VGroup(
        Line(UL * size, DR * size, color=theme.INCORRECT, stroke_width=theme.STROKE_THICK),
        Line(UR * size, DL * size, color=theme.INCORRECT, stroke_width=theme.STROKE_THICK),
    )
    return VGroup(circle, cross)
