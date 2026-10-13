"""Text helpers: titles, subtitles, body text, labels and section labels.

All helpers return ordinary Manim ``Text`` objects (or small groups), so you
can still call ``.next_to()``, ``.shift()``, ``.set_color()`` etc. on them.
"""

from manim import DOWN, LEFT, UL, UP, Line, Text, VGroup

from src.themes import default_theme as theme


def create_title(text: str, color: str = theme.TEXT_PRIMARY) -> Text:
    """Large bold heading, placed at the top of the frame.

    Use once per scene/section, e.g. ``create_title("Natural Numbers")``.
    """
    title = Text(text, font=theme.FONT, font_size=theme.TITLE_SIZE, color=color, weight="BOLD")
    return title.to_edge(UP, buff=theme.MARGIN)


def create_subtitle(text: str, color: str = theme.TEXT_SECONDARY) -> Text:
    """Smaller, softer line of text that usually sits under a title.

    It is not positioned; place it yourself, e.g.
    ``create_subtitle("...").next_to(title, DOWN)``.
    """
    return Text(text, font=theme.FONT, font_size=theme.SUBTITLE_SIZE, color=color)


def create_body_text(text: str, color: str = theme.TEXT_PRIMARY) -> Text:
    """Normal explanatory text. Use ``\\n`` inside ``text`` for line breaks."""
    return Text(text, font=theme.FONT, font_size=theme.BODY_SIZE, color=color, line_spacing=1.2)


def create_label(text: str, color: str = theme.TEXT_SECONDARY) -> Text:
    """Small caption for pointing at things (arrows, number-line points, shapes)."""
    return Text(text, font=theme.FONT, font_size=theme.LABEL_SIZE, color=color)


def create_highlighted_text(text: str, color: str = theme.HIGHLIGHT) -> Text:
    """Body-sized text in the highlight colour, for a key word or term."""
    return Text(text, font=theme.FONT, font_size=theme.BODY_SIZE, color=color, weight="BOLD")


def create_section_label(text: str, color: str = theme.ACCENT) -> VGroup:
    """Small upper-case tag with an accent underline, pinned to the top-left.

    Good for telling students which part of the lesson they are in,
    e.g. ``create_section_label("Example 1")``.
    """
    label = Text(text.upper(), font=theme.FONT, font_size=theme.SECTION_LABEL_SIZE, color=color, weight="BOLD")
    underline = Line(label.get_left(), label.get_right(), color=color, stroke_width=theme.STROKE_THIN)
    underline.next_to(label, DOWN, buff=theme.SPACING_SMALL / 2).align_to(label, LEFT)
    return VGroup(label, underline).to_corner(UL, buff=theme.MARGIN)
