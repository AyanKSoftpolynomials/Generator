"""Box and card helpers."""

from manim import Mobject, RoundedRectangle, SurroundingRectangle, VGroup

from src.components.text import create_body_text
from src.themes import default_theme as theme


def create_highlight_box(target: Mobject, color: str = theme.HIGHLIGHT, buff: float = theme.SPACING_SMALL) -> SurroundingRectangle:
    """Rounded outline drawn around an existing object to draw attention to it.

    Typical use: ``self.play(Create(create_highlight_box(equation)))``.
    """
    return SurroundingRectangle(
        target,
        color=color,
        buff=buff,
        corner_radius=theme.CORNER_RADIUS,
        stroke_width=theme.STROKE_NORMAL,
    )


def create_info_box(text: str, color: str = theme.IMPORTANT) -> VGroup:
    """Filled card with a coloured border containing ``text``.

    Use for "Remember:" / "Important:" information. Returns
    ``VGroup(box, text)`` so both move together.
    """
    content = create_body_text(text)
    box = RoundedRectangle(
        corner_radius=theme.CORNER_RADIUS,
        width=content.width + 2 * theme.BOX_PADDING,
        height=content.height + 2 * theme.BOX_PADDING,
        stroke_color=color,
        stroke_width=theme.STROKE_NORMAL,
        fill_color=theme.BOX_FILL,
        fill_opacity=theme.BOX_FILL_OPACITY,
    )
    content.move_to(box)
    return VGroup(box, content)
