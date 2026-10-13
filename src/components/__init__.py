"""Reusable visual building blocks for lesson scenes.

Import everything at once in a lesson:

    from src.components import *
"""

from src.components.arrows import create_arrow, create_curved_arrow, create_pointer
from src.components.common import fit_to_frame, stack
from src.components.equations import create_equation, highlight_part
from src.components.highlights import create_correct_indicator, create_incorrect_indicator, create_underline
from src.components.number_line import create_number_line, mark_number
from src.components.shapes import create_highlight_box, create_info_box
from src.components.text import (
    create_body_text,
    create_highlighted_text,
    create_label,
    create_section_label,
    create_subtitle,
    create_title,
)

__all__ = [
    "create_arrow",
    "create_curved_arrow",
    "create_pointer",
    "fit_to_frame",
    "stack",
    "create_equation",
    "highlight_part",
    "create_correct_indicator",
    "create_incorrect_indicator",
    "create_underline",
    "create_number_line",
    "mark_number",
    "create_highlight_box",
    "create_info_box",
    "create_body_text",
    "create_highlighted_text",
    "create_label",
    "create_section_label",
    "create_subtitle",
    "create_title",
]
