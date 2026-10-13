"""Equation helpers (LaTeX via ``MathTex``; needs MiKTeX/LaTeX installed)."""

from manim import MathTex

from src.themes import default_theme as theme


def create_equation(*tex_parts: str, color: str = theme.EQUATION, font_size: float = theme.EQUATION_SIZE) -> MathTex:
    """Build a maths expression from LaTeX strings.

    Passing several parts lets you colour or animate each part separately:

        eq = create_equation("1", "+", "2", "=", "3")
        eq[4].set_color(theme.CORRECT)     # colour only the "3"

    Remember to use raw strings for backslashes: ``create_equation(r"\\frac{1}{2}")``.
    """
    return MathTex(*tex_parts, color=color, font_size=font_size)


def highlight_part(equation: MathTex, index: int, color: str = theme.HIGHLIGHT) -> MathTex:
    """Colour one part of an equation built with ``create_equation`` and return it."""
    equation[index].set_color(color)
    return equation
