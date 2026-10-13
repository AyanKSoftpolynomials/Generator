"""Number line helpers."""

from manim import UP, Dot, NumberLine, VGroup

from src.components.text import create_label
from src.themes import default_theme as theme


def create_number_line(
    start: float = 0,
    end: float = 10,
    step: float = 1,
    length: float = 11,
    include_numbers: bool = True,
    color: str = theme.NUMBER_LINE,
) -> NumberLine:
    """Horizontal number line from ``start`` to ``end`` with a tick every ``step``.

    Convert a value to a screen position with ``line.n2p(3)`` ("number to point"),
    which is how you place dots, arrows and labels on it.
    """
    line = NumberLine(
        x_range=[start, end, step],
        length=length,
        include_numbers=include_numbers,
        include_tip=False,
        color=color,
        stroke_width=theme.STROKE_NORMAL,
        font_size=theme.LABEL_SIZE + 6,
    )
    if include_numbers:
        line.numbers.set_color(color)
    return line


def mark_number(line: NumberLine, value: float, color: str = theme.HIGHLIGHT, label: str | None = None) -> VGroup:
    """Return a dot (and optional text label above it) at ``value`` on ``line``."""
    dot = Dot(line.n2p(value), color=color, radius=0.1)
    group = VGroup(dot)
    if label is not None:
        group.add(create_label(label, color=color).next_to(dot, UP, buff=theme.SPACING_MEDIUM))
    return group
