"""Layout validation: text fits its box, objects stay in frame, no collisions, readable sizes."""

from src.validation.layout import DEFAULT_CONFIG, ERROR, INFO, WARNING, Issue, LayoutValidator
from src.validation.report import format_report

__all__ = ["DEFAULT_CONFIG", "ERROR", "INFO", "WARNING", "Issue", "LayoutValidator", "format_report"]
