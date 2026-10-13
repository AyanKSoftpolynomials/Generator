from manim import *
from src.animation.lms_scene import LMSScene


class EfficiencyRatioVideo(LMSScene):
    """
    Efficiency Ratio
    C-CAT | Section A | Module 2: Quantitative Aptitude | Day 4
    Time and Work > Efficiency and Time Comparison

    Visual concept:
        efficiency  = unit BLOCKS          (A = 3 blue, B = 2 orange)
        the job     = a WALL               (together: 6 days -> 6 equal day-chunks)
        one day of joint work is sliced into 5 slivers, one per block
                    -> one unit = 1/30 of the wall per day
        A = 3 slivers a day -> 10 days      B = 2 slivers a day -> 15 days

    Narration/audio/subtitle metadata is registered through self.narrate().
    The video generator handles TTS, voice selection, audio duration,
    WhisperX alignment, subtitles, timing and final composition.
    Every run_time here is a share of self.duration_of(n), so the visuals
    stretch or shrink with the real narration length.
    """

    # ---------------------------------------------------------
    # THEME
    # ---------------------------------------------------------

    BG = "#07090F"
    WHITE = "#FFFFFF"
    YELLOW = "#FFD54A"      # one unit / answers
    BLUE = "#4FC3F7"        # A / machine 1
    ORANGE = "#FFB74D"      # B / machine 2
    GREEN = "#69F0AE"       # working together
    RED = "#FF5252"
    PURPLE = "#B388FF"
    GREY = "#8A93A6"
    GRID = "#141A26"

    WALL_W = 10.0
    WALL_H = 0.55
    VOICE = "teacher_a"

    def construct(self):

        self.camera.background_color = self.BG
        self.bg = self.backdrop()
        self.add(self.bg)

        self.hook()
        self.introduction()
        self.how()
        self.what()
        self.why()
        self.real_world_example()
        self.summary()
        self.done()

    # =========================================================
    # COMMON HELPERS
    # =========================================================

    def say(self, id, text, voice=None):
        return self.narrate(id=id, text=text, voice=voice or self.VOICE, subtitle=True)

    def rt(self, n, share):
        """A share of the narration's real duration (never shorter than 0.3 s)."""
        return max(0.3, self.duration_of(n) * share)

    def backdrop(self):
        """Faint engineering grid: gives depth without competing with content."""
        lines = VGroup()
        for x in np.arange(-8, 8.01, 1.0):
            lines.add(Line([x, -4.5, 0], [x, 4.5, 0], stroke_color=self.GRID, stroke_width=1))
        for y in np.arange(-4, 4.01, 1.0):
            lines.add(Line([-8, y, 0], [8, y, 0], stroke_color=self.GRID, stroke_width=1))
        return lines

    def title_text(self, text, color=None, size=52):
        return Text(text, font_size=size, color=color or self.WHITE, weight=BOLD)

    def label(self, text, color=None, size=30):
        return Text(text, font_size=size, color=color or self.WHITE)

    def tex(self, *parts, colors=None, size=44):
        """MathTex split into parts so each part can carry its own color."""
        m = MathTex(*parts, font_size=size, color=self.WHITE)
        for i, c in (colors or {}).items():
            m[i].set_color(c)
        return m

    def glow(self, mob, color, layers=8, width=22, opacity=0.06):
        """Soft halo: stacked translucent strokes behind a mobject."""
        halo = VGroup()
        for i in range(1, layers + 1):
            halo.add(mob.copy().set_fill(opacity=0).set_stroke(color, width=width * i / layers, opacity=opacity))
        return halo

    def shine(self, mob, color, run_time):
        """Fade a glow in behind `mob` and keep `mob` on top."""
        halo = self.glow(mob, color)
        self.play(FadeIn(halo), run_time=run_time)
        self.add(mob)
        return halo

    def sweep(self, mob, color, run_time, buff=0.15):
        """A bright light sweeping around a frame: the 'shining' highlight."""
        frame = SurroundingRectangle(mob, buff=buff, corner_radius=0.1).set_stroke(color, 5)
        self.play(ShowPassingFlash(frame, time_width=0.6), run_time=run_time)

    def blocks(self, n, color, side=0.3, buff=0.05):
        """n efficiency units."""
        return VGroup(*[
            Square(side_length=side, stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=0.9)
            for _ in range(n)
        ]).arrange(RIGHT, buff=buff)

    def bar(self, center):
        return Rectangle(width=self.WALL_W, height=self.WALL_H, stroke_color=self.GREY,
                         stroke_width=2).move_to(center)

    def span(self, bar, start, count, total, color, opacity=0.8):
        """Filled piece covering cells [start, start + count) of a bar cut into `total`."""
        w = bar.width / total
        rect = Rectangle(width=count * w, height=bar.height, stroke_color=self.BG, stroke_width=2,
                         fill_color=color, fill_opacity=opacity)
        rect.move_to([bar.get_left()[0] + (start + count / 2) * w, bar.get_y(), 0])
        return rect

    def cut_lines(self, bar, total):
        w = bar.width / total
        x0 = bar.get_left()[0]
        return VGroup(*[
            Line([x0 + i * w, bar.get_top()[1], 0], [x0 + i * w, bar.get_bottom()[1], 0],
                 stroke_color=self.GREY, stroke_width=1)
            for i in range(1, total)
        ])

    def person(self, color):
        head = Circle(radius=0.32, color=self.YELLOW, stroke_width=3)
        body = Line(DOWN * 0.32, DOWN * 1.2, color=color, stroke_width=6)
        arms = VGroup(
            Line(DOWN * 0.6, DOWN * 0.9 + LEFT * 0.5, color=color, stroke_width=5),
            Line(DOWN * 0.6, DOWN * 0.9 + RIGHT * 0.5, color=color, stroke_width=5),
        )
        legs = VGroup(
            Line(DOWN * 1.2, DOWN * 1.7 + LEFT * 0.35, color=color, stroke_width=5),
            Line(DOWN * 1.2, DOWN * 1.7 + RIGHT * 0.35, color=color, stroke_width=5),
        )
        return VGroup(head, body, arms, legs)

    def lock(self, color, scale=1.0):
        body = RoundedRectangle(corner_radius=0.06, width=0.46, height=0.36,
                                fill_color=color, fill_opacity=1, stroke_width=0)
        shackle = Arc(radius=0.15, start_angle=0, angle=PI, stroke_color=color, stroke_width=5)
        shackle.move_arc_center_to(body.get_top() + UP * 0.07)
        legs = VGroup(
            Line(shackle.get_start(), shackle.get_start() + DOWN * 0.09),
            Line(shackle.get_end(), shackle.get_end() + DOWN * 0.09),
        ).set_stroke(color, 5)
        hole = Dot(body.get_center(), radius=0.045, color=self.BG)
        return VGroup(VGroup(shackle, legs), body, hole).scale(scale)

    def unlock_anims(self, lk):
        return [
            lk[0].animate.shift(UP * lk.height * 0.25).set_color(self.GREEN),
            lk[1].animate.set_fill(self.GREEN),
        ]

    def clock(self, radius=0.8):
        face = Circle(radius=radius, color=self.WHITE, stroke_width=3)
        ticks = VGroup(*[
            Line(UP * radius * 0.84, UP * radius, color=self.GREY, stroke_width=2).rotate(a, about_point=ORIGIN)
            for a in np.arange(0, TAU, TAU / 12)
        ])
        hands = VGroup(
            Line(ORIGIN, UP * radius * 0.62, color=self.YELLOW, stroke_width=4),
            Line(ORIGIN, RIGHT * radius * 0.42, color=self.YELLOW, stroke_width=4),
        )
        return VGroup(face, ticks, hands, Dot(radius=0.05, color=self.YELLOW))

    def on_screen(self):
        """Top-level mobjects except the backdrop, without double-counting children."""
        mobs = [m for m in self.mobjects if m is not self.bg]
        children = {id(sm) for m in mobs for sm in m.get_family()[1:]}
        return [m for m in mobs if id(m) not in children]

    def clear(self, run_time):
        mobs = self.on_screen()
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)

    def slide_board(self, new_group, direction, run_time):
        """Old board slides out, new board slides in: feels like a camera pan."""
        old = self.on_screen()
        new_group.shift(-direction * 16)
        self.add(new_group)
        self.play(*[m.animate.shift(direction * 16) for m in old],
                  new_group.animate.shift(direction * 16), run_time=run_time)
        self.remove(*old)

    # =========================================================
    # 1. HOOK
    # =========================================================

    def hook(self):

        self.scene_start("hook")

        # -----------------------------------------------------
        # Narration 1
        # -----------------------------------------------------

        n = self.say("hook_01", "Hello again, my dear students!")

        greeting = self.title_text("Hello again, my dear students!", color=self.YELLOW, size=46)
        self.play(FadeIn(greeting, shift=UP * 0.3), run_time=self.rt(n, 0.4))
        halo = self.shine(greeting, self.YELLOW, self.rt(n, 0.3))
        self.wait_for_narration(n)
        self.play(FadeOut(greeting), FadeOut(halo), run_time=0.35)

        # -----------------------------------------------------
        # Narration 2 — the puzzle, as a picture
        # -----------------------------------------------------

        n = self.say(
            "hook_02",
            "A and B have an efficiency ratio of 3 to 2, and together, "
            "they finish a job in 6 days.",
        )

        self.ratio = self.tex("A", ":", "B", "=", "3", ":", "2", size=54,
                              colors={0: self.BLUE, 2: self.ORANGE, 4: self.BLUE, 6: self.ORANGE})
        self.ratio.move_to(UP * 3.2)
        self.a_blocks = self.blocks(3, self.BLUE).move_to([-1.3, 2.35, 0])
        self.b_blocks = self.blocks(2, self.ORANGE).move_to([1.1, 2.35, 0])

        self.wall = self.bar([0, 1.0, 0])
        wall_lbl = self.tex("A", "+", "B", size=36, colors={0: self.BLUE, 2: self.ORANGE})
        wall_lbl.next_to(self.wall, LEFT, buff=0.3)
        # together: 6 days -> 6 equal day-chunks (each chunk = 5 of 30 cells)
        self.day_chunks = VGroup(*[self.span(self.wall, 5 * i, 5, 30, self.GREEN, 0.55) for i in range(6)])
        self.days_lbl = MathTex(r"6\text{ days}", font_size=34, color=self.GREEN)
        self.days_lbl.next_to(self.wall, RIGHT, buff=0.25)

        self.play(Write(self.ratio), run_time=self.rt(n, 0.15))
        self.play(
            LaggedStart(*[FadeIn(s, scale=0.4) for s in [*self.a_blocks, *self.b_blocks]], lag_ratio=0.2),
            run_time=self.rt(n, 0.15),
        )
        self.play(Create(self.wall), FadeIn(wall_lbl), run_time=self.rt(n, 0.1))
        self.play(LaggedStart(*[FadeIn(c) for c in self.day_chunks], lag_ratio=0.5), run_time=self.rt(n, 0.3))
        self.play(FadeIn(self.days_lbl, shift=LEFT * 0.1), run_time=self.rt(n, 0.08))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3
        # -----------------------------------------------------

        n = self.say("hook_03", "How long would each take alone?")

        self.a_bar = self.bar([0, -0.6, 0])
        self.b_bar = self.bar([0, -1.9, 0])
        self.a_lbl = self.tex("A", size=40, colors={0: self.BLUE}).next_to(self.a_bar, LEFT, buff=0.35)
        self.b_lbl = self.tex("B", size=40, colors={0: self.ORANGE}).next_to(self.b_bar, LEFT, buff=0.35)
        self.q_a = MathTex("?", font_size=46, color=self.BLUE).next_to(self.a_bar, RIGHT, buff=0.3)
        self.q_b = MathTex("?", font_size=46, color=self.ORANGE).next_to(self.b_bar, RIGHT, buff=0.3)

        self.play(Create(self.a_bar), Create(self.b_bar), FadeIn(self.a_lbl, self.b_lbl),
                  run_time=self.rt(n, 0.4))
        self.play(Write(self.q_a), Write(self.q_b), run_time=self.rt(n, 0.25))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 4
        # -----------------------------------------------------

        n = self.say("hook_04", "Let's use the ratio directly.")

        self.sweep(self.ratio, self.YELLOW, self.rt(n, 0.5))

        self.wait_for_narration(n)

    # =========================================================
    # 2. INTRODUCTION
    # =========================================================

    def introduction(self):

        self.scene_start("introduction")

        n = self.say(
            "intro_01",
            "Welcome to our first stop — Efficiency Ratio — solving from a ratio "
            "given directly, not from exact days.",
        )

        # a dark veil lets the title shine without destroying the board beneath
        veil = FullScreenRectangle(fill_color=self.BG, fill_opacity=0.85, stroke_width=0)
        title = self.title_text("EFFICIENCY RATIO", color=self.YELLOW, size=64).move_to(UP * 0.4)
        sub = self.label("from a ratio given directly — not from exact days", color=self.GREY, size=28)
        sub.next_to(title, DOWN, buff=0.4)

        self.play(FadeIn(veil), run_time=self.rt(n, 0.08))
        self.play(FadeIn(title, scale=1.1), run_time=self.rt(n, 0.15))
        halo = self.shine(title, self.YELLOW, self.rt(n, 0.1))
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=self.rt(n, 0.12))

        self.wait_for_narration(n)

        # title retires to the corner; the puzzle board comes back
        corner = self.title_text("Efficiency Ratio", color=self.GREY, size=26).to_corner(UL, buff=0.35)
        self.play(ReplacementTransform(title, corner), FadeOut(halo), FadeOut(sub), FadeOut(veil), run_time=0.7)
        self.corner_title = corner

    # =========================================================
    # 3. HOW
    # =========================================================

    def how(self):

        self.scene_start("how")

        chunk = self.day_chunks[0]

        # -----------------------------------------------------
        # Narration 1 — isolate one day of joint work
        # -----------------------------------------------------

        n = self.say("how_01", "So how do we use a given ratio?")

        self.play(self.day_chunks[1:].animate.set_fill(opacity=0.12),
                  self.days_lbl.animate.set_opacity(0.3), run_time=self.rt(n, 0.35))
        self.sweep(chunk, self.GREEN, self.rt(n, 0.3), buff=0.08)

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — total units
        # -----------------------------------------------------

        n = self.say(
            "how_02",
            'My dear students, add the ratio\'s two numbers together to get the '
            'total number of "efficiency units,"',
        )

        row = VGroup(self.a_blocks.copy(), self.b_blocks.copy()).arrange(RIGHT, buff=0.05)
        row.next_to(chunk, UP, buff=0.55)
        self.play(self.a_blocks.animate.move_to(row[0]), self.b_blocks.animate.move_to(row[1]),
                  run_time=self.rt(n, 0.25))
        units_row = VGroup(self.a_blocks, self.b_blocks)
        self.units_brace = Brace(units_row, UP, buff=0.08, color=self.GREY)
        self.units_lbl = self.label("total units", color=self.GREY, size=22).next_to(self.units_brace, UP, buff=0.08)
        self.play(GrowFromCenter(self.units_brace), FadeIn(self.units_lbl), run_time=self.rt(n, 0.2))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — magnify that day, cut it into one sliver per unit
        # -----------------------------------------------------

        n = self.say("how_03", "then divide the combined rate by that total to find what one unit is worth.")

        solo_parts = VGroup(self.a_bar, self.b_bar, self.a_lbl, self.b_lbl, self.q_a, self.q_b)
        self.play(solo_parts.animate.set_opacity(0.12), run_time=self.rt(n, 0.08))

        self.inset = Rectangle(width=5.0, height=1.65, stroke_color=self.GREEN, stroke_width=3,
                               fill_color=self.GREEN, fill_opacity=0.22).move_to([0, -1.3, 0])
        self.zoom_lines = VGroup(
            DashedLine(chunk.get_corner(DL), self.inset.get_corner(UL), color=self.GREY, stroke_width=1.5),
            DashedLine(chunk.get_corner(DR), self.inset.get_corner(UR), color=self.GREY, stroke_width=1.5),
        )
        self.play(Create(self.zoom_lines), TransformFromCopy(chunk, self.inset), run_time=self.rt(n, 0.2))

        # the magnified blocks sit exactly above their slivers: one unit, one sliver
        self.inset_blocks = VGroup(*[
            Square(side_length=0.8, stroke_width=2, fill_opacity=0.9,
                   stroke_color=c, fill_color=c).move_to([-2.0 + i * 1.0, 0.03, 0])
            for i, c in enumerate([self.BLUE] * 3 + [self.ORANGE] * 2)
        ])
        self.play(TransformFromCopy(VGroup(*self.a_blocks, *self.b_blocks), self.inset_blocks),
                  run_time=self.rt(n, 0.15))
        self.inset_cuts = self.cut_lines(self.inset, 5).set_stroke(self.WHITE, 2)
        self.play(Create(self.inset_cuts), run_time=self.rt(n, 0.15))

        self.rule = MathTex(r"\text{one unit} = \frac{\text{combined rate}}{\text{total units}}", font_size=40)
        self.rule.move_to(DOWN * 3.2)
        self.play(Write(self.rule), run_time=self.rt(n, 0.2))

        self.wait_for_narration(n)

    # =========================================================
    # 4. WHAT
    # =========================================================

    def what(self):

        self.scene_start("what")

        # -----------------------------------------------------
        # Narration 1 — 3 + 2 = 5
        # -----------------------------------------------------

        n = self.say("what_01", "Ratio 3 to 2 gives 5 total units.")

        self.eq = self.tex("3", "+", "2", "=", "5", colors={0: self.BLUE, 2: self.ORANGE, 4: self.YELLOW})
        self.eq.move_to([-0.6, 2.1, 0])
        self.play(FadeOut(self.rule),
                  TransformFromCopy(self.ratio[4], self.eq[0]),
                  TransformFromCopy(self.ratio[6], self.eq[2]),
                  FadeIn(self.eq[1]), run_time=self.rt(n, 0.3))
        self.play(Write(self.eq[3:]), run_time=self.rt(n, 0.2))
        five_lbl = self.label("5 units", color=self.YELLOW, size=22).move_to(self.units_lbl)
        self.play(Transform(self.units_lbl, five_lbl), run_time=self.rt(n, 0.15))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — one unit = 1/6 ÷ 5 = 1/30
        # -----------------------------------------------------

        n = self.say(
            "what_02",
            "Combined rate is 1 over 6, so one unit equals 1 over 6, divided by 5, "
            "which is 1 over 30.",
        )

        sixth = MathTex(r"\tfrac{1}{6}", font_size=44, color=self.GREEN).next_to(self.inset, LEFT, buff=0.35)
        self.play(FadeIn(sixth, shift=RIGHT * 0.1), run_time=self.rt(n, 0.08))

        eq2 = self.tex(r"\frac{1}{6}", r"\div", "5", "=", r"\frac{1}{30}",
                       colors={0: self.GREEN, 2: self.YELLOW, 4: self.YELLOW}).move_to(self.eq)
        self.play(TransformMatchingShapes(self.eq, eq2), run_time=self.rt(n, 0.15))
        self.eq = eq2

        # every unit fills its own sliver
        w = self.inset.width / 5
        inset_fill = VGroup(*[
            Rectangle(width=w, height=self.inset.height, stroke_color=self.BG, stroke_width=2,
                      fill_color=c, fill_opacity=0.9).move_to([self.inset.get_left()[0] + (i + 0.5) * w, self.inset.get_y(), 0])
            for i, c in enumerate([self.BLUE] * 3 + [self.ORANGE] * 2)
        ])
        self.play(TransformFromCopy(self.inset_blocks, inset_fill), run_time=self.rt(n, 0.15))

        one = MathTex(r"\tfrac{1}{30}", font_size=40, color=self.YELLOW).next_to(inset_fill[0], DOWN, buff=0.2)
        self.play(FadeIn(one, shift=UP * 0.1), Indicate(inset_fill[0], color=self.YELLOW, scale_factor=1.15),
                  run_time=self.rt(n, 0.1))
        halo = self.shine(one, self.YELLOW, self.rt(n, 0.07))

        # the magnified view collapses back into the real wall
        self.colored = VGroup(*[
            self.span(self.wall, i, 1, 30, c, 0.9) for i, c in enumerate([self.BLUE] * 3 + [self.ORANGE] * 2)
        ])
        self.play(
            ReplacementTransform(inset_fill, self.colored),
            FadeOut(self.inset, self.inset_blocks, self.inset_cuts, self.zoom_lines, sixth, one, halo),
            run_time=self.rt(n, 0.18),
        )
        solo_parts = VGroup(self.a_bar, self.b_bar, self.a_lbl, self.b_lbl, self.q_a, self.q_b)
        self.play(solo_parts.animate.set_opacity(1), run_time=self.rt(n, 0.07))
        self.thirtieths = self.cut_lines(self.wall, 30)
        self.play(Create(self.thirtieths, lag_ratio=0.05), run_time=self.rt(n, 0.1))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narrations 3 & 4 — each person alone
        # -----------------------------------------------------

        self.a_answer = self.solo(
            "what_03",
            "A, with 3 units, has a rate of 3 over 30, or 1 over 10 — taking 10 days alone.",
            self.a_bar, self.colored[0:3], 3, self.BLUE, 10, self.q_a,
            ("3", r"\times", r"\frac{1}{30}", "=", r"\frac{3}{30}", "=", r"\frac{1}{10}"),
        )
        self.b_answer = self.solo(
            "what_04",
            "B, with 2 units, has a rate of 2 over 30, or 1 over 15 — taking 15 days alone.",
            self.b_bar, self.colored[3:5], 2, self.ORANGE, 15, self.q_b,
            ("2", r"\times", r"\frac{1}{30}", "=", r"\frac{2}{30}", "=", r"\frac{1}{15}"),
        )

    def solo(self, id, text, bar, own_slivers, units, color, days, question, parts):
        """One person alone: their day's slivers repeat until the wall is full."""

        n = self.say(id, text)

        eq = self.tex(*parts, colors={0: color, 2: self.YELLOW, 4: color, 6: color}).move_to(DOWN * 3.1)
        chunks = VGroup(*[self.span(bar, units * i, units, 30, color, 0.9 if i == 0 else 0.55) for i in range(days)])
        counts = VGroup(*[
            MathTex(str(i + 1), font_size=20 if days <= 10 else 16, color=self.BG).move_to(c)
            for i, c in enumerate(chunks)
        ])
        answer = MathTex(rf"{days}\text{{ days}}", font_size=36, color=self.YELLOW).next_to(bar, RIGHT, buff=0.25)

        self.play(TransformFromCopy(own_slivers, chunks[0]), run_time=self.rt(n, 0.12))
        if hasattr(self, "solo_eq"):
            self.play(TransformMatchingShapes(self.solo_eq, eq[0:5]), run_time=self.rt(n, 0.15))
        else:
            self.play(Write(eq[0:5]), run_time=self.rt(n, 0.15))
        self.play(Write(eq[5:]), run_time=self.rt(n, 0.1))
        self.solo_eq = eq
        self.play(
            LaggedStart(*[FadeIn(c) for c in chunks[1:]], lag_ratio=0.3),
            LaggedStart(*[FadeIn(k) for k in counts], lag_ratio=0.3),
            run_time=self.rt(n, 0.3),
        )
        self.play(ReplacementTransform(question, answer), Flash(answer, color=self.YELLOW, flash_radius=0.7),
                  run_time=self.rt(n, 0.12))
        self.shine(answer, self.YELLOW, self.rt(n, 0.06))

        self.wait_for_narration(n)
        return answer

    # =========================================================
    # 5. WHY
    # =========================================================

    def why(self):

        self.scene_start("why")

        n = self.say("why_01", "Now, why does this matter?")

        answers = VGroup(self.a_answer, self.b_answer)
        self.play(FadeOut(self.solo_eq), run_time=self.rt(n, 0.2))
        self.sweep(answers, self.YELLOW, self.rt(n, 0.35))

        self.wait_for_narration(n)

        n = self.say(
            "why_02",
            "Because questions often give you a ratio directly, expecting you to unlock "
            "exact individual times from it — exactly the reverse of finding a ratio from known times.",
        )

        self.sweep(self.ratio, self.YELLOW, self.rt(n, 0.12))
        unlock = CurvedArrow(self.ratio.get_right() + RIGHT * 0.2, self.a_answer.get_top() + UP * 0.15,
                             angle=-PI / 2.6, color=self.YELLOW, stroke_width=5)
        lk = self.lock(self.YELLOW, scale=1.3).move_to([5.7, 2.35, 0])
        unlock_lbl = self.label("unlock", color=self.YELLOW, size=26).next_to(lk, DOWN, buff=0.15)
        self.play(Create(unlock), FadeIn(lk), run_time=self.rt(n, 0.18))
        self.play(*self.unlock_anims(lk), FadeIn(unlock_lbl), run_time=self.rt(n, 0.12))
        self.play(Indicate(answers, color=self.YELLOW), run_time=self.rt(n, 0.12))

        reverse = CurvedArrow(self.a_answer.get_top() + UP * 0.15 + LEFT * 0.45,
                              self.ratio.get_right() + RIGHT * 0.2 + DOWN * 0.25,
                              angle=PI / 3.5, color=self.GREY, stroke_width=3)
        reverse_lbl = self.label("reverse", color=self.GREY, size=24).move_to([3.5, 1.5, 0])
        self.play(Create(reverse), FadeIn(reverse_lbl), run_time=self.rt(n, 0.18))

        self.wait_for_narration(n)

    # =========================================================
    # 6. REAL WORLD EXAMPLE
    # =========================================================

    def real_world_example(self):

        self.scene_start("real_world")

        # -----------------------------------------------------
        # Narration 1 — slide to a fresh board
        # -----------------------------------------------------

        n = self.say(
            "example_01",
            "Let me tell you about a girl named Avantika, told that two machines have an "
            "efficiency ratio of 5 to 3, and together produce a batch in 4 hours.",
        )

        avantika = self.person(self.PURPLE).scale(0.75).move_to([-5.9, 1.9, 0])
        name = self.label("Avantika", color=self.YELLOW, size=26).next_to(avantika, DOWN, buff=0.2)
        items = VGroup(*[Circle(radius=0.17, stroke_color=self.GREY, stroke_width=2) for _ in range(32)])
        items.arrange_in_grid(rows=4, cols=8, buff=0.16).move_to([0.8, -0.1, 0])
        batch_lbl = self.label("BATCH", color=self.GREY, size=20).next_to(items, UP, buff=0.2).align_to(items, LEFT)

        self.slide_board(VGroup(avantika, name, items, batch_lbl), LEFT, self.rt(n, 0.18))

        ratio2 = self.tex("M_1", ":", "M_2", "=", "5", ":", "3", size=50,
                          colors={0: self.BLUE, 2: self.ORANGE, 4: self.BLUE, 6: self.ORANGE}).move_to([0.8, 3.2, 0])
        m1 = self.blocks(5, self.BLUE).move_to([-0.6, 2.35, 0])
        m2 = self.blocks(3, self.ORANGE).move_to([2.3, 2.35, 0])
        together = MathTex(r"\text{together: } 4\text{ h}", font_size=36, color=self.GREEN).move_to([4.9, 1.5, 0])

        self.play(Write(ratio2), run_time=self.rt(n, 0.15))
        self.play(LaggedStart(*[FadeIn(s, scale=0.4) for s in [*m1, *m2]], lag_ratio=0.1), run_time=self.rt(n, 0.15))
        self.play(FadeIn(together, shift=DOWN * 0.1), run_time=self.rt(n, 0.1))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — 8 units, one row of the batch per hour
        # -----------------------------------------------------

        n = self.say("example_02", "She found 8 total units, with the combined rate of 1 over 4 divided among them,")

        total = self.tex("5", "+", "3", "=", "8", colors={0: self.BLUE, 2: self.ORANGE, 4: self.YELLOW})
        total.move_to([-4.7, -0.8, 0])
        self.play(TransformFromCopy(ratio2[4], total[0]), TransformFromCopy(ratio2[6], total[2]),
                  FadeIn(total[1], total[3:]), run_time=self.rt(n, 0.2))

        # one hour together = one row; each unit makes one item
        made = VGroup(*[
            items[i].copy().set_fill(self.BLUE if i < 5 else self.ORANGE, opacity=0.9)
            .set_stroke(self.BLUE if i < 5 else self.ORANGE)
            for i in range(8)
        ])
        self.play(TransformFromCopy(VGroup(*m1, *m2), made), run_time=self.rt(n, 0.2))
        brace = Brace(VGroup(*items[0:8]), RIGHT, buff=0.1, color=self.GREEN)
        hour = MathTex(r"1\text{ h} = \tfrac{1}{4}", font_size=30, color=self.GREEN).next_to(brace, RIGHT, buff=0.1)
        self.play(GrowFromCenter(brace), FadeIn(hour), run_time=self.rt(n, 0.12))

        unit = self.tex(r"\frac{1}{4}", r"\div", "8", "=", r"\frac{1}{32}",
                        colors={0: self.GREEN, 2: self.YELLOW, 4: self.YELLOW}, size=40).move_to([-4.7, -2.1, 0])
        self.play(Write(unit), run_time=self.rt(n, 0.2))
        self.shine(unit[4], self.YELLOW, self.rt(n, 0.06))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — individual rates, then individual times
        # -----------------------------------------------------

        n = self.say("example_03", "giving each machine's individual rate, and from there, their individual times.")

        rest = [
            AnimationGroup(*[
                items[8 * r + i].animate.set_fill(self.BLUE if i < 5 else self.ORANGE, opacity=0.45)
                .set_stroke(self.BLUE if i < 5 else self.ORANGE)
                for i in range(8)
            ])
            for r in range(1, 4)
        ]
        self.play(LaggedStart(*rest, lag_ratio=0.4), run_time=self.rt(n, 0.15))

        line1 = self.tex("M_1", r":\;", r"5 \times \tfrac{1}{32} = \tfrac{5}{32}", r"\;\Rightarrow\;",
                         r"\tfrac{32}{5}\text{ h}", colors={0: self.BLUE, 4: self.YELLOW}, size=38)
        line2 = self.tex("M_2", r":\;", r"3 \times \tfrac{1}{32} = \tfrac{3}{32}", r"\;\Rightarrow\;",
                         r"\tfrac{32}{3}\text{ h}", colors={0: self.ORANGE, 4: self.YELLOW}, size=38)
        VGroup(line1, line2).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to([2.2, -2.8, 0])

        self.play(Write(line1[0:3]), run_time=self.rt(n, 0.15))
        self.play(Write(line1[3:]), run_time=self.rt(n, 0.1))
        self.play(Write(line2[0:3]), run_time=self.rt(n, 0.15))
        self.play(Write(line2[3:]), run_time=self.rt(n, 0.1))
        self.sweep(VGroup(line1[4], line2[4]), self.YELLOW, self.rt(n, 0.12), buff=0.12)

        self.wait_for_narration(n)

    # =========================================================
    # 7. SUMMARY
    # =========================================================

    def summary(self):

        self.scene_start("summary")

        n = self.say("summary_01", "So here's what we take away today.")

        summary_title = self.title_text("THE TAKEAWAY", color=self.YELLOW, size=50).to_edge(UP, buff=0.6)
        self.slide_board(VGroup(summary_title), UP, self.rt(n, 0.35))
        self.shine(summary_title, self.YELLOW, self.rt(n, 0.2))

        self.wait_for_narration(n)

        n = self.say(
            "summary_02",
            "Add the ratio's numbers for total units, divide the combined rate by that total "
            "for one unit's value, then multiply back out for each person's individual rate.",
        )

        steps = VGroup(
            self.tex(r"\text{total units}", "=", "a", "+", "b", colors={2: self.BLUE, 4: self.ORANGE}),
            self.tex(r"\text{one unit}", "=", r"{\text{combined rate} \over \text{total units}}", colors={0: self.YELLOW}),
            self.tex(r"\text{rate}_A", "=", "a", r"\times", r"\text{one unit}",
                     colors={0: self.BLUE, 2: self.BLUE, 4: self.YELLOW}),
        ).arrange(DOWN, buff=0.65, aligned_edge=LEFT).move_to(DOWN * 0.4 + RIGHT * 0.5)

        badges = VGroup()
        for i, s in enumerate(steps, start=1):
            disc = Circle(radius=0.28, color=self.YELLOW, fill_color=self.YELLOW, fill_opacity=1)
            num = Text(str(i), font_size=26, color=self.BG, weight=BOLD).move_to(disc)
            badges.add(VGroup(disc, num).next_to(s, LEFT, buff=0.5))

        for badge, step in zip(badges, steps):
            self.play(FadeIn(badge, scale=0.6), Write(step), run_time=self.rt(n, 0.22))
        self.sweep(steps[2], self.YELLOW, self.rt(n, 0.12))

        self.wait_for_narration(n)

    # =========================================================
    # 8. DONE / TRANSITION TO TIME RATIO
    # =========================================================

    def done(self):

        self.scene_start("done")

        n = self.say("done_01", "That's Efficiency Ratio for you — a given ratio, fully unlocked.")

        self.clear(self.rt(n, 0.12))
        ratio = self.tex("3", ":", "2", size=96, colors={0: self.BLUE, 2: self.ORANGE}).move_to(UP * 0.3)
        lk = self.lock(self.YELLOW, scale=2.2).next_to(ratio, UP, buff=0.35)
        self.play(FadeIn(ratio, scale=0.8), FadeIn(lk), run_time=self.rt(n, 0.18))
        self.play(*self.unlock_anims(lk), run_time=self.rt(n, 0.15))
        a_time = MathTex(r"A:\ 10\text{ days}", font_size=44, color=self.BLUE).move_to([-3.2, -1.8, 0])
        b_time = MathTex(r"B:\ 15\text{ days}", font_size=44, color=self.ORANGE).move_to([3.2, -1.8, 0])
        self.play(TransformFromCopy(ratio[0], a_time), TransformFromCopy(ratio[2], b_time), run_time=self.rt(n, 0.2))
        self.play(Flash(a_time, color=self.BLUE, flash_radius=1.0),
                  Flash(b_time, color=self.ORANGE, flash_radius=1.0), run_time=self.rt(n, 0.12))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Next lesson transition
        # -----------------------------------------------------

        n = self.say("done_02", "In our next video, we approach the very same idea from time instead — Time Ratio.")

        self.clear(self.rt(n, 0.12))
        nxt = self.label("NEXT VIDEO", color=self.GREY, size=26).move_to(UP * 2.4)
        topic = self.title_text("TIME RATIO", color=self.YELLOW, size=64).next_to(nxt, DOWN, buff=0.3)
        clk = self.clock().move_to(DOWN * 1.0)
        self.play(FadeIn(nxt, shift=DOWN * 0.2), run_time=self.rt(n, 0.1))
        self.play(FadeIn(topic, scale=1.1), run_time=self.rt(n, 0.15))
        self.shine(topic, self.YELLOW, self.rt(n, 0.1))
        self.play(FadeIn(clk, scale=0.7), run_time=self.rt(n, 0.1))
        self.play(Rotate(clk[2], angle=-TAU / 3, about_point=clk[0].get_center()), run_time=self.rt(n, 0.25))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Final narration
        # -----------------------------------------------------

        n = self.say("done_03", "See you there!")

        see_you = self.title_text("SEE YOU THERE!", color=self.YELLOW, size=56).move_to(DOWN * 2.9)
        self.play(FadeIn(see_you, scale=1.1), run_time=self.rt(n, 0.5))
        self.shine(see_you, self.YELLOW, self.rt(n, 0.3))

        self.wait_for_narration(n)

        self.clear(0.8)

        self.scene_end("done")