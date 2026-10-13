"""Tiny scene that only proves the toolchain works (not lesson content).

Render it with:

    python scripts/render_preview.py tests/test_scene.py

It exercises Text (Pango fonts), MathTex (LaTeX), the theme, the component
helpers and video encoding.
"""

from manim import DOWN, FadeIn, FadeOut, Scene, Write

from src.components import create_equation, create_title
from src.themes import default_theme as theme


class HelloStudents(Scene):
    def construct(self):
        title = create_title("Hello Students!")
        equation = create_equation("1", "+", "2", "=", "3")
        equation[4].set_color(theme.CORRECT)

        self.play(Write(title), run_time=theme.ANIM_NORMAL)
        self.play(FadeIn(equation, shift=DOWN * 0.3), run_time=theme.ANIM_NORMAL)
        self.wait(theme.PAUSE)
        self.play(FadeOut(title), FadeOut(equation), run_time=theme.ANIM_FAST)
