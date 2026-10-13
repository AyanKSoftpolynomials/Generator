"""
Points in Space: a short demo of the two animation engines in one lesson.

  * Manim (default) for the flat, 2D idea: a point on a plane needs two numbers.
  * Blender for the part where 3D has real teaching value: the third direction.
    The camera swings around so the depth is visible, and the point moves
    exactly when each direction is spoken (word timings from WhisperX).
  * Manim again for the formula summary.

Generate:  python generate.py lessons/blender_demo/animation.py
"""

from manim import *

from src.animation import BLENDER, LMSScene
from src.blender import BlenderScene

BG = "#0E1726"
X_COLOR, Y_COLOR, Z_COLOR = "#FF6B6B", "#51CF66", "#38BDF8"
POINT = "#FFD166"
TEACHER = "teacher_a"


class PointInSpace(BlenderScene):
    """3D section: axes, a point walking x -> y -> z, guide lines, orbiting camera."""

    background = BG

    def construct(self, b, t):
        b.axes(length=4, ticks=4, colors=(X_COLOR, Y_COLOR, Z_COLOR))
        point = b.sphere(radius=0.2, color=POINT, emission=0.8)
        b.grow_in(point, start=0.2, duration=0.5)

        # Each move starts when its direction is spoken (fallbacks if a word is missing).
        steps = [
            ((3, 0, 0), t.word("along x", default=t.duration * 0.25), X_COLOR, (0, 0, 0)),
            ((3, 2, 0), t.word("along y", default=t.duration * 0.45), Y_COLOR, (3, 0, 0)),
            ((3, 2, 2), t.word("along z", default=t.duration * 0.65), Z_COLOR, (3, 2, 0)),
        ]
        for target, at, color, origin in steps:
            b.move(point, to=target, start=at, duration=1.2)
            guide = b.line(origin, target, thickness=0.035, color=color, emission=0.6)
            b.appear(guide, at + 1.2)

        label = b.point_label("(3, 2, 2)", at=(3, 2, 2), size=0.5, color=POINT)
        b.appear(label, steps[-1][1] + 1.3)
        b.orbit_camera(radius=14, height=6.5, start=0, end=t.duration, start_angle=-40, end_angle=25,
                       look_at=(1.2, 0.8, 0.8))


class PointsInSpaceVideo(LMSScene):
    lesson_title = "Points in Space"
    default_voice = TEACHER

    def construct(self):
        # ------------------------------------------------ 1. flat plane (Manim)
        self.scene_start("plane", title="Two Numbers on a Plane")
        title = Text("Points in Space", font_size=46, weight=BOLD).to_edge(UP)
        plane = NumberPlane(x_range=[-1, 5, 1], y_range=[-1, 4, 1], x_length=6, y_length=5,
                            background_line_style={"stroke_opacity": 0.3}).shift(DOWN * 0.4)
        dot = Dot(plane.c2p(3, 2), color=POINT, radius=0.1)
        label = MathTex("(3,\\ 2)", color=POINT).next_to(dot, UR, buff=0.15)
        n = self.narrate("plane_01", "On a flat page, two numbers are enough to find any point: "
                                     "three steps across, and two steps up.")
        self.play(FadeIn(title), Create(plane), run_time=1.5)
        self.at_word(n, "three steps")
        self.play(FadeIn(dot, scale=2), Write(label), run_time=1.2)
        self.wait_for_narration(n)
        self.play(FadeOut(VGroup(title, plane, dot, label)), run_time=0.6)

        # ------------------------------------------------ 2. into space (Blender)
        self.scene_start("space", title="The Third Direction", engine=BLENDER)
        n = self.narrate("space_01", "Now step into space. From the origin, go three steps along x, "
                                     "then two steps along y, and finally two steps up along z. "
                                     "Three directions, three numbers.")
        self.blender(PointInSpace, narration=n)

        # ------------------------------------------------ 3. summary (Manim)
        self.scene_start("summary", title="Summary")
        formula = MathTex("(", "x", ",\\ ", "y", ",\\ ", "z", ")", font_size=96)
        formula[1].set_color(X_COLOR)
        formula[3].set_color(Y_COLOR)
        formula[5].set_color(Z_COLOR)
        caption = Text("every point in space", font_size=34).next_to(formula, DOWN, buff=0.6)
        n = self.narrate("summary_01", "So every point in space is written with three coordinates: x, y and z.")
        self.play_with(n, Write(formula), FadeIn(caption, shift=UP * 0.2), fraction=0.5)
        self.wait_for_narration(n, include_pause=False)
