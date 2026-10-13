"""Small layout helpers shared by lessons and other components."""

from manim import DOWN, Mobject, VGroup, config

from src.themes import default_theme as theme


def stack(*mobjects: Mobject, direction=DOWN, buff: float = theme.SPACING_MEDIUM) -> VGroup:
    """Group objects and lay them out in a row/column (default: top to bottom)."""
    return VGroup(*mobjects).arrange(direction, buff=buff)


def fit_to_frame(mobject: Mobject, margin: float = theme.MARGIN) -> Mobject:
    """Shrink ``mobject`` (never enlarge) so it fits inside the frame margins.

    Useful for long equations or sentences that would run off screen.
    """
    max_width = config.frame_width - 2 * margin
    max_height = config.frame_height - 2 * margin
    if mobject.width > max_width:
        mobject.scale_to_fit_width(max_width)
    if mobject.height > max_height:
        mobject.scale_to_fit_height(max_height)
    return mobject
