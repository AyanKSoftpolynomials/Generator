import math

from manim import *
from src.animation.lms_scene import LMSScene


class TrailingZerosVideo(LMSScene):
    """
    Trailing Zeros
    C-CAT | Section A | Module 2: Quantitative Aptitude | Day 3
    Number Systems > Factorials

    Visual concept:
        the real 158-digit value of 100! on screen — impossible by hand
        every trailing zero = one hidden (2 x 5) pair = a factor of 10
        2s vastly outnumber 5s, so the 5s decide the count
        a 10 x 10 grid of 1..100:  multiples of 5 get one ring  (20)
                                   multiples of 25 get a second ring (4)
        20 + 4 = 24 rings = 24 trailing zeros

    Narration/audio/subtitle metadata is registered through self.narrate().
    The video generator handles TTS, voice selection, audio duration,
    WhisperX alignment, subtitles, timing and final composition.
    Every run_time is a share of self.duration_of(n).
    """

    # ---------------------------------------------------------
    # THEME
    # ---------------------------------------------------------

    BG = "#07090F"
    WHITE = "#FFFFFF"
    YELLOW = "#FFD54A"      # zeros / answers
    GREEN = "#69F0AE"       # factor 2
    ORANGE = "#FFB74D"      # factor 5 (first ring)
    PINK = "#FF80AB"        # extra 5 from 25 (second ring)
    BLUE = "#4FC3F7"
    RED = "#FF5252"
    PURPLE = "#B388FF"
    GREY = "#8A93A6"
    GRID = "#141A26"

    VOICE = "teacher_a"
    MONO = "Consolas"

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
        return max(0.3, self.duration_of(n) * share)

    def backdrop(self):
        lines = VGroup()
        for x in np.arange(-8, 8.01, 1.0):
            lines.add(Line([x, -4.5, 0], [x, 4.5, 0], stroke_color=self.GRID, stroke_width=1))
        for y in np.arange(-4, 4.01, 1.0):
            lines.add(Line([-8, y, 0], [8, y, 0], stroke_color=self.GRID, stroke_width=1))
        return lines

    def title_text(self, text, color=None, size=52):
        return Text(text, font_size=size, color=color or self.WHITE, weight=BOLD)

    def label(self, text, color=None, size=30, weight=NORMAL):
        return Text(text, font_size=size, color=color or self.WHITE, weight=weight)

    def tex(self, *parts, colors=None, size=44):
        m = MathTex(*parts, font_size=size, color=self.WHITE)
        for i, c in (colors or {}).items():
            m[i].set_color(c)
        return m

    def glow(self, mob, color, layers=8, width=22, opacity=0.06):
        halo = VGroup()
        for i in range(1, layers + 1):
            halo.add(mob.copy().set_fill(opacity=0).set_stroke(color, width=width * i / layers, opacity=opacity))
        return halo

    def shine(self, mob, color, run_time):
        halo = self.glow(mob, color)
        self.play(FadeIn(halo), run_time=run_time)
        self.add(mob)
        return halo

    def sweep(self, mob, color, run_time, buff=0.15):
        frame = SurroundingRectangle(mob, buff=buff, corner_radius=0.1).set_stroke(color, 5)
        self.play(ShowPassingFlash(frame, time_width=0.6), run_time=run_time)

    def on_screen(self):
        mobs = [m for m in self.mobjects if m is not self.bg]
        children = {id(sm) for m in mobs for sm in m.get_family()[1:]}
        return [m for m in mobs if id(m) not in children]

    def clear(self, run_time, keep=()):
        keep_ids = {id(sm) for k in keep for sm in k.get_family()}
        mobs = [m for m in self.on_screen() if id(m) not in keep_ids]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)

    def slide_board(self, new_group, direction, run_time):
        old = self.on_screen()
        new_group.shift(-direction * 16)
        self.add(new_group)
        self.play(*[m.animate.shift(direction * 16) for m in old],
                  new_group.animate.shift(direction * 16), run_time=run_time)
        self.remove(*old)

    def check_mark(self, color=None, scale=1.0):
        return VMobject().set_points_as_corners(
            [[-0.22, 0.02, 0], [-0.06, -0.16, 0], [0.24, 0.2, 0]]
        ).set_stroke(color or self.GREEN, 6).scale(scale)

    def person(self, color):
        head = Circle(radius=0.32, color=self.YELLOW, stroke_width=3)
        body = Line(DOWN * 0.32, DOWN * 1.2, color=color, stroke_width=6)
        arms = VGroup(Line(DOWN * 0.6, DOWN * 0.9 + LEFT * 0.5, color=color, stroke_width=5),
                      Line(DOWN * 0.6, DOWN * 0.9 + RIGHT * 0.5, color=color, stroke_width=5))
        legs = VGroup(Line(DOWN * 1.2, DOWN * 1.7 + LEFT * 0.35, color=color, stroke_width=5),
                      Line(DOWN * 1.2, DOWN * 1.7 + RIGHT * 0.35, color=color, stroke_width=5))
        return VGroup(head, body, arms, legs)

    def open_with_greeting(self):
        n = self.say("hook_01", "Hello again, my dear students!")
        greeting = self.title_text("Hello again, my dear students!", color=self.YELLOW, size=46)
        self.play(FadeIn(greeting, shift=UP * 0.3), run_time=self.rt(n, 0.4))
        halo = self.shine(greeting, self.YELLOW, self.rt(n, 0.3))
        self.wait_for_narration(n)
        self.play(FadeOut(greeting, halo), run_time=0.35)

    def see_you_there(self):
        n = self.say("done_03", "See you there.")
        bye = self.title_text("SEE YOU THERE!", color=self.YELLOW, size=56).move_to(DOWN * 2.9)
        self.play(FadeIn(bye, scale=1.1), run_time=self.rt(n, 0.5))
        self.shine(bye, self.YELLOW, self.rt(n, 0.3))
        self.wait_for_narration(n)
        self.clear(0.8)

    # ---------- lesson-specific visuals ----------

    def factorial_digits(self, n, per_line=40, size=24, width=12.4):
        """The true decimal value of n!, wrapped into monospace lines."""
        s = str(math.factorial(n))
        lines = VGroup(*[Text(s[i:i + per_line], font=self.MONO, font_size=size, color=self.GREY)
                         for i in range(0, len(s), per_line)])
        lines.arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        if lines.width > width:
            lines.scale_to_fit_width(width)
        lines.digit_count = len(s)
        lines.trailing = len(s) - len(s.rstrip("0"))
        return lines

    def trailing_glyphs(self, lines):
        """The glyphs of the trailing zeros (all in the last line for 100!)."""
        return lines[-1][-lines.trailing:]

    def number_grid(self, count, cols=10, cell=0.5, center=ORIGIN):
        cells = VGroup()
        for v in range(1, count + 1):
            sq = Square(side_length=cell, stroke_color=self.GRID, stroke_width=1.5, fill_color="#0D1320",
                        fill_opacity=1)
            num = Text(str(v), font_size=int(cell * 30), color=self.GREY).move_to(sq)
            cells.add(VGroup(sq, num))
        cells.arrange_in_grid(rows=count // cols, cols=cols, buff=0)
        return cells.move_to(center)

    def ring(self, cell, color, inset=0.0):
        side = cell[0].width - inset
        return Square(side_length=side, stroke_color=color, stroke_width=3.5).move_to(cell)

    def factor_block(self, text, color, side=0.7):
        sq = RoundedRectangle(corner_radius=0.1, width=side, height=side, stroke_color=color, stroke_width=3,
                              fill_color=color, fill_opacity=0.2)
        return VGroup(sq, MathTex(text, font_size=int(side * 55), color=color).move_to(sq))

    def stopwatch(self, radius=0.7):
        face = Circle(radius=radius, stroke_color=self.WHITE, stroke_width=4)
        button = RoundedRectangle(corner_radius=0.05, width=0.3, height=0.18, stroke_width=0,
                                  fill_color=self.WHITE, fill_opacity=1).next_to(face, UP, buff=0.02)
        hand = Line(ORIGIN, UP * radius * 0.75, stroke_color=self.YELLOW, stroke_width=5)
        w = VGroup(face, button, hand, Dot(radius=0.05, color=self.YELLOW))
        w.hand, w.face = hand, face
        return w

    # =========================================================
    # 1. HOOK
    # =========================================================

    def hook(self):

        self.scene_start("hook")

        self.open_with_greeting()

        # -----------------------------------------------------
        # Narration 2 — the real 100!
        # -----------------------------------------------------

        n = self.say("hook_02", "How many zeroes does 100 factorial end with?")

        head = self.tex("100!", "=", r"1 \times 2 \times 3 \times \cdots \times 100", size=44,
                        colors={0: self.YELLOW}).move_to(UP * 2.9)
        self.digits = self.factorial_digits(100).move_to(UP * 0.4)
        self.play(Write(head), run_time=self.rt(n, 0.25))
        self.play(AddTextLetterByLetter(self.digits[0]), run_time=self.rt(n, 0.12))
        self.play(*[FadeIn(line) for line in self.digits[1:]], run_time=self.rt(n, 0.12))
        count = self.label(f"{self.digits.digit_count} digits", color=self.GREY, size=24)
        count.next_to(self.digits, DOWN, buff=0.35).align_to(self.digits, LEFT)
        q = Text("how many zeros at the end?", font_size=30, color=self.YELLOW, weight=BOLD)
        q.next_to(self.digits, DOWN, buff=0.35).align_to(self.digits, RIGHT)
        self.play(FadeIn(count), FadeIn(q, shift=UP * 0.1), run_time=self.rt(n, 0.12))
        self.head, self.hook_q, self.count_lbl = head, q, count

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — not by hand, but under a minute
        # -----------------------------------------------------

        n = self.say(
            "hook_03",
            "You certainly won't calculate that enormous number by hand... "
            "and yet, we'll answer this in under a minute.",
        )

        cross = VGroup(Line(self.digits.get_corner(UL), self.digits.get_corner(DR)),
                       Line(self.digits.get_corner(UR), self.digits.get_corner(DL))).set_stroke(self.RED, 6)
        by_hand = self.label("by hand?", color=self.RED, size=28, weight=BOLD).next_to(self.digits, UP, buff=0.2)
        self.play(Create(cross), FadeIn(by_hand), run_time=self.rt(n, 0.2))
        self.play(FadeOut(cross, by_hand), self.digits.animate.set_opacity(0.35), run_time=self.rt(n, 0.12))

        watch = self.stopwatch().move_to([0, -2.6, 0])
        under = self.label("< 1 minute", color=self.YELLOW, size=30, weight=BOLD).next_to(watch, RIGHT, buff=0.4)
        self.play(FadeOut(self.count_lbl, self.hook_q), FadeIn(watch, scale=0.8), FadeIn(under), run_time=self.rt(n, 0.15))
        self.play(Rotate(watch.hand, angle=-TAU * 0.8, about_point=watch.face.get_center()), run_time=self.rt(n, 0.25),
                  rate_func=linear)
        self.watch, self.under = watch, under

        self.wait_for_narration(n)

    # =========================================================
    # 2. INTRODUCTION
    # =========================================================

    def introduction(self):

        self.scene_start("introduction")

        n = self.say("intro_01", "Welcome back! Today we meet the elegant trick for counting Trailing Zeros in any factorial.")

        self.play(FadeOut(self.head, self.watch, self.under), self.digits.animate.set_opacity(1).move_to(DOWN * 1.2),
                  run_time=self.rt(n, 0.15))
        title = self.title_text("TRAILING ZEROS", color=self.YELLOW, size=64).move_to(UP * 2.3)
        self.play(FadeIn(title, scale=1.1), run_time=self.rt(n, 0.15))
        self.shine(title, self.YELLOW, self.rt(n, 0.1))

        # the zeros at the very end of the number light up — this is what we count
        tail = self.trailing_glyphs(self.digits)
        self.play(tail.animate.set_color(self.YELLOW), run_time=self.rt(n, 0.15))
        brace = Brace(tail, DOWN, buff=0.12, color=self.YELLOW)
        brace_q = Text("?", font_size=40, color=self.YELLOW, weight=BOLD).next_to(brace, DOWN, buff=0.1)
        self.play(GrowFromCenter(brace), Write(brace_q), run_time=self.rt(n, 0.15))
        self.shine(tail, self.YELLOW, self.rt(n, 0.08))

        self.wait_for_narration(n)

    # =========================================================
    # 3. HOW — pairs of 2 and 5, and the 5s decide
    # =========================================================

    def how(self):

        self.scene_start("how")

        n = self.say("how_01", "So how does this trick work?")

        self.clear(self.rt(n, 0.3))
        eq = self.tex("10", "=", "2", r"\times", "5", size=64, colors={0: self.YELLOW, 2: self.GREEN, 4: self.ORANGE})
        eq.move_to(UP * 2.5)
        self.play(Write(eq), run_time=self.rt(n, 0.3))

        self.wait_for_narration(n)

        n = self.say(
            "how_02",
            "My dear students, every trailing zero comes from a hidden pair of 2 and 5 inside that giant multiplication.",
        )

        # each (2, 5) pair snaps into a 10, and a zero appears on the end of the number
        tail_num = VGroup(Text("…", font_size=48, color=self.GREY)).move_to([2.6, 0.3, 0])
        pairs = VGroup()
        for k in range(3):
            two = self.factor_block("2", self.GREEN).move_to([-4.8, 0.8 - k * 1.1, 0])
            five = self.factor_block("5", self.ORANGE).move_to([-3.8, 0.8 - k * 1.1, 0])
            pairs.add(VGroup(two, five))
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in pairs], lag_ratio=0.2), FadeIn(tail_num),
                  run_time=self.rt(n, 0.2))
        zeros = VGroup()
        for k, p in enumerate(pairs):
            ten = self.factor_block("10", self.YELLOW, side=0.8).move_to([-1.4, p.get_y(), 0])
            self.play(ReplacementTransform(p, ten), run_time=self.rt(n, 0.1))
            z = Text("0", font=self.MONO, font_size=48, color=self.YELLOW, weight=BOLD)
            z.next_to(VGroup(tail_num, *zeros), RIGHT, buff=0.08)
            self.play(TransformFromCopy(ten, z), FadeOut(ten), run_time=self.rt(n, 0.1))
            zeros.add(z)
        self.shine(zeros, self.YELLOW, self.rt(n, 0.06))
        self.how_clutter = VGroup(tail_num, zeros)

        self.wait_for_narration(n)

        n = self.say(
            "how_03",
            "Since 2s are always far more common than 5s, we simply need to count how many 5s are hiding inside.",
        )

        self.play(FadeOut(self.how_clutter), run_time=self.rt(n, 0.08))
        # true counts inside 100!: 2 appears 97 times, 5 appears 24 times (numbers left off on purpose)
        unit = 0.085
        bar2 = Rectangle(width=97 * unit, height=0.55, stroke_width=0, fill_color=self.GREEN, fill_opacity=0.8)
        bar5 = Rectangle(width=24 * unit, height=0.55, stroke_width=0, fill_color=self.ORANGE, fill_opacity=0.9)
        bar2.move_to([0, 0.6, 0]).align_to([-4.2, 0, 0], LEFT)
        bar5.move_to([0, -0.5, 0]).align_to([-4.2, 0, 0], LEFT)
        lbl2 = self.label("2s inside 100!", color=self.GREEN, size=24).next_to(bar2, LEFT, buff=0.25)
        lbl5 = self.label("5s inside 100!", color=self.ORANGE, size=24).next_to(bar5, LEFT, buff=0.25)
        self.play(GrowFromEdge(bar2, LEFT), FadeIn(lbl2), run_time=self.rt(n, 0.18))
        self.play(GrowFromEdge(bar5, LEFT), FadeIn(lbl5), run_time=self.rt(n, 0.12))
        limit = DashedLine(bar5.get_corner(UR) + UP * 1.3, bar5.get_corner(DR) + DOWN * 0.3, color=self.YELLOW)
        limit_lbl = self.label("pairs run out here", color=self.YELLOW, size=22).next_to(limit, DOWN, buff=0.1)
        spare = self.label("spare 2s", color=self.GREY, size=22).move_to([2.8, 1.3, 0])
        self.play(Create(limit), FadeIn(limit_lbl), FadeIn(spare), run_time=self.rt(n, 0.15))
        count5 = self.label("so: count the 5s", color=self.ORANGE, size=34, weight=BOLD).move_to(DOWN * 2.5)
        self.play(FadeIn(count5, shift=UP * 0.2), run_time=self.rt(n, 0.12))
        self.shine(count5, self.ORANGE, self.rt(n, 0.06))

        self.wait_for_narration(n)

    # =========================================================
    # 4. WHAT — counting the 5s in 1..100
    # =========================================================

    def what(self):

        self.scene_start("what")

        grid = self.number_grid(100, cell=0.5, center=[-3.3, 0.2, 0])
        mult5 = [grid[v - 1] for v in range(5, 101, 5)]
        mult25 = [grid[v - 1] for v in range(25, 101, 25)]

        # -----------------------------------------------------
        # Narration 1 — multiples of 5: one ring each
        # -----------------------------------------------------

        n = self.say("what_01", "For 100 factorial, count multiples of 5 up to 100, which gives 20,")

        self.clear(self.rt(n, 0.08))
        self.play(FadeIn(grid, lag_ratio=0.01), run_time=self.rt(n, 0.2))
        rings5 = VGroup(*[self.ring(c, self.ORANGE, inset=0.06) for c in mult5])
        self.play(LaggedStart(*[Create(r) for r in rings5], lag_ratio=0.08), run_time=self.rt(n, 0.3))
        c5 = self.tex(r"\frac{100}{5}", "=", "20", size=48, colors={2: self.ORANGE}).move_to([3.5, 1.9, 0])
        cap5 = self.label("multiples of 5", color=self.ORANGE, size=22).next_to(c5, LEFT, buff=0.4)
        self.play(Write(c5), FadeIn(cap5), run_time=self.rt(n, 0.2))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — multiples of 25: a second ring
        # -----------------------------------------------------

        n = self.say("what_02", "then multiples of 25, which gives 4 more, since each contributes an extra 5.")

        rings25 = VGroup(*[self.ring(c, self.PINK, inset=0.16) for c in mult25])
        self.play(LaggedStart(*[Create(r) for r in rings25], lag_ratio=0.2), run_time=self.rt(n, 0.2))
        split = self.tex("25", "=", "5", r"\times", "5", size=40, colors={2: self.ORANGE, 4: self.PINK})
        split.move_to([3.5, -1.8, 0])
        self.play(Write(split), Indicate(VGroup(*mult25), color=self.PINK), run_time=self.rt(n, 0.2))
        c25 = self.tex(r"\frac{100}{25}", "=", "4", size=48, colors={2: self.PINK}).move_to([3.5, 0.5, 0])
        cap25 = self.label("multiples of 25", color=self.PINK, size=22).next_to(c25, LEFT, buff=0.4)
        self.play(Write(c25), FadeIn(cap25), run_time=self.rt(n, 0.2))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — 24 rings, 24 zeros
        # -----------------------------------------------------

        n = self.say(
            "what_03",
            "Adding these together, 20 plus 4, gives us 24 trailing zeroes — "
            "found without ever calculating that enormous number itself.",
        )

        self.play(FadeOut(split), run_time=self.rt(n, 0.05))
        total = self.tex("20", "+", "4", "=", "24", size=60,
                         colors={0: self.ORANGE, 2: self.PINK, 4: self.YELLOW}).move_to([3.5, -0.9, 0])
        self.play(TransformFromCopy(c5[2], total[0]), TransformFromCopy(c25[2], total[2]), FadeIn(total[1]),
                  run_time=self.rt(n, 0.15))
        self.play(Write(total[3:]), run_time=self.rt(n, 0.1))
        self.shine(total[4], self.YELLOW, self.rt(n, 0.06))

        # every ring becomes one zero
        zeros = VGroup(*[Text("0", font=self.MONO, font_size=30, color=self.YELLOW, weight=BOLD) for _ in range(24)])
        zeros.arrange(RIGHT, buff=0.06).move_to([0, -3.35, 0])
        self.play(LaggedStart(*[ReplacementTransform(r.copy(), z) for r, z in zip([*rings5, *rings25], zeros)],
                              lag_ratio=0.04), run_time=self.rt(n, 0.3))
        zeros_lbl = self.label("24 trailing zeros", color=self.YELLOW, size=22, weight=BOLD).next_to(zeros, UP, buff=0.12)
        self.play(FadeIn(zeros_lbl), run_time=self.rt(n, 0.06))
        self.sweep(zeros, self.YELLOW, self.rt(n, 0.08), buff=0.08)

        self.wait_for_narration(n)

    # =========================================================
    # 5. WHY — the exam clock
    # =========================================================

    def why(self):

        self.scene_start("why")

        n = self.say("why_01", "Now, why does this matter?")

        self.clear(self.rt(n, 0.25))
        watch = self.stopwatch(radius=0.8).move_to(UP * 2.4)
        self.play(FadeIn(watch, scale=0.8), run_time=self.rt(n, 0.2))
        self.play(Rotate(watch.hand, angle=-TAU * 0.3, about_point=watch.face.get_center()), run_time=self.rt(n, 0.2))

        self.wait_for_narration(n)

        n = self.say(
            "why_02",
            "Because factorial-based questions specifically test whether you know this shortcut — "
            "without it, a seemingly simple question becomes practically impossible within exam time.",
        )

        slow = self.factorial_digits(100, per_line=20, size=20, width=5.2).move_to([-3.4, -0.6, 0])
        slow_lbl = self.label("without the shortcut", color=self.RED, size=26, weight=BOLD).next_to(slow, UP, buff=0.3)
        fast = self.tex(r"\frac{100}{5} + \frac{100}{25}", "=", "24", size=46, colors={2: self.YELLOW})
        fast.move_to([3.4, -0.6, 0])
        fast_lbl = self.label("with the shortcut", color=self.GREEN, size=26, weight=BOLD).next_to(fast, UP, buff=0.5)

        self.play(FadeIn(slow_lbl), FadeIn(slow, lag_ratio=0.1), run_time=self.rt(n, 0.2))
        self.play(Rotate(watch.hand, angle=-TAU * 1.5, about_point=watch.face.get_center()),
                  watch.face.animate.set_stroke(self.RED), run_time=self.rt(n, 0.2), rate_func=linear)
        impossible = self.label("out of time", color=self.RED, size=24).next_to(slow, DOWN, buff=0.3)
        self.play(FadeIn(impossible), slow.animate.set_opacity(0.35), run_time=self.rt(n, 0.08))
        self.play(FadeIn(fast_lbl), Write(fast), watch.face.animate.set_stroke(self.GREEN), run_time=self.rt(n, 0.15))
        tick = self.check_mark(self.GREEN, 1.5).next_to(fast, DOWN, buff=0.4)
        self.play(Create(tick), run_time=self.rt(n, 0.08))
        self.shine(fast, self.GREEN, self.rt(n, 0.06))

        self.wait_for_narration(n)

    # =========================================================
    # 6. REAL WORLD EXAMPLE — 50!
    # =========================================================

    def real_world_example(self):

        self.scene_start("real_world")

        grid = self.number_grid(50, cell=0.5, center=[-2.4, 0.9, 0])
        mult5 = [grid[v - 1] for v in range(5, 51, 5)]
        mult25 = [grid[v - 1] for v in range(25, 51, 25)]

        n = self.say("example_01", "Let me tell you about a girl named Kimaya, asked to find the trailing zeroes in 50 factorial.")

        kimaya = self.person(self.PURPLE).scale(0.55).move_to([-6.3, -1.8, 0])
        name = self.label("Kimaya", color=self.YELLOW, size=22).next_to(kimaya, RIGHT, buff=0.2)
        self.slide_board(VGroup(kimaya, name), LEFT, self.rt(n, 0.18))
        q = self.tex(r"50!", r"\text{ ends in how many zeros?}", size=40, colors={0: self.YELLOW}).move_to([3.4, 3.1, 0])
        self.play(Write(q), run_time=self.rt(n, 0.2))
        self.play(FadeIn(grid, lag_ratio=0.02), run_time=self.rt(n, 0.2))

        self.wait_for_narration(n)

        n = self.say(
            "example_02",
            "She counted multiples of 5 up to 50, giving 10, then multiples of 25, giving 2 more.",
        )

        rings5 = VGroup(*[self.ring(c, self.ORANGE, inset=0.06) for c in mult5])
        rings25 = VGroup(*[self.ring(c, self.PINK, inset=0.16) for c in mult25])
        c5 = self.tex(r"\frac{50}{5}", "=", "10", size=46, colors={2: self.ORANGE}).move_to([4.0, 1.5, 0])
        c25 = self.tex(r"\frac{50}{25}", "=", "2", size=46, colors={2: self.PINK}).move_to([4.0, 0.1, 0])
        self.play(LaggedStart(*[Create(r) for r in rings5], lag_ratio=0.1), run_time=self.rt(n, 0.2))
        self.play(Write(c5), run_time=self.rt(n, 0.15))
        self.play(LaggedStart(*[Create(r) for r in rings25], lag_ratio=0.3), run_time=self.rt(n, 0.12))
        self.play(Write(c25), run_time=self.rt(n, 0.15))

        self.wait_for_narration(n)

        n = self.say("example_03", "Adding these, 10 plus 2, gave her 12 trailing zeroes, reached calmly and quickly.")

        total = self.tex("10", "+", "2", "=", "12", size=58,
                         colors={0: self.ORANGE, 2: self.PINK, 4: self.YELLOW}).move_to([4.0, -1.3, 0])
        self.play(TransformFromCopy(c5[2], total[0]), TransformFromCopy(c25[2], total[2]), FadeIn(total[1]),
                  run_time=self.rt(n, 0.18))
        self.play(Write(total[3:]), run_time=self.rt(n, 0.12))
        zeros = VGroup(*[Text("0", font=self.MONO, font_size=34, color=self.YELLOW, weight=BOLD) for _ in range(12)])
        zeros.arrange(RIGHT, buff=0.06).move_to([0.6, -2.8, 0])
        self.play(LaggedStart(*[ReplacementTransform(r.copy(), z) for r, z in zip([*rings5, *rings25], zeros)],
                              lag_ratio=0.06), run_time=self.rt(n, 0.25))
        self.shine(total[4], self.YELLOW, self.rt(n, 0.08))

        self.wait_for_narration(n)

    # =========================================================
    # 7. SUMMARY
    # =========================================================

    def summary(self):

        self.scene_start("summary")

        n = self.say("summary_01", "So here's what we take away today.")

        summary_title = self.title_text("THE TAKEAWAY", color=self.YELLOW, size=50).to_edge(UP, buff=0.5)
        self.slide_board(VGroup(summary_title), UP, self.rt(n, 0.35))
        self.shine(summary_title, self.YELLOW, self.rt(n, 0.2))

        self.wait_for_narration(n)

        n = self.say(
            "summary_02",
            "To count trailing zeroes, count the multiples of 5, then 25, then 125, and so on, "
            "adding them all together.",
        )

        # the ladder of divisors: each rung is 5 times the last
        rungs = VGroup(*[self.factor_block(v, c, side=1.1) for v, c in
                         [("5", self.ORANGE), ("25", self.PINK), ("125", self.PURPLE)]])
        rungs.add(MathTex(r"\cdots", font_size=60, color=self.GREY))
        rungs.arrange(RIGHT, buff=1.1).move_to(UP * 0.9)
        steps = VGroup(*[
            VGroup(Arrow(rungs[i].get_right(), rungs[i + 1].get_left(), buff=0.1, color=self.GREY, stroke_width=3),
                   MathTex(r"\times 5", font_size=28, color=self.GREY))
            for i in range(3)
        ])
        for s in steps:
            s[1].next_to(s[0], UP, buff=0.05)
        rule = self.tex("Z", "=", r"\frac{n}{5}", "+", r"\frac{n}{25}", "+", r"\frac{n}{125}", "+", r"\cdots",
                        size=56, colors={0: self.YELLOW, 2: self.ORANGE, 4: self.PINK, 6: self.PURPLE})
        rule.move_to(DOWN * 1.5)
        note = self.label("count whole multiples only", color=self.GREY, size=22).next_to(rule, DOWN, buff=0.35)

        self.play(FadeIn(rungs[0], shift=UP * 0.2), run_time=self.rt(n, 0.1))
        for i in range(3):
            self.play(GrowArrow(steps[i][0]), FadeIn(steps[i][1]), FadeIn(rungs[i + 1], shift=UP * 0.2),
                      run_time=self.rt(n, 0.1))
        self.play(Write(rule), run_time=self.rt(n, 0.25))
        self.play(FadeIn(note), run_time=self.rt(n, 0.06))
        self.sweep(rule, self.YELLOW, self.rt(n, 0.1))

        self.wait_for_narration(n)

    # =========================================================
    # 8. DONE
    # =========================================================

    def done(self):

        self.scene_start("done")

        n = self.say("done_01", "That's Trailing Zeros for you — rapid growth, elegantly tamed.")

        self.clear(self.rt(n, 0.12))
        digits = self.factorial_digits(100).move_to(UP * 0.8)
        tamed = MathTex(r"\rightarrow\; 24", r"\text{ zeros}", font_size=56, color=self.YELLOW).move_to(DOWN * 1.6)
        self.play(FadeIn(digits, lag_ratio=0.05), run_time=self.rt(n, 0.25))
        self.play(self.trailing_glyphs(digits).animate.set_color(self.YELLOW), run_time=self.rt(n, 0.12))
        self.play(TransformFromCopy(self.trailing_glyphs(digits), tamed), run_time=self.rt(n, 0.2))
        self.shine(tamed, self.YELLOW, self.rt(n, 0.1))

        self.wait_for_narration(n)

        n = self.say("done_02", "In our next video, we go one level deeper — Factors in Factorial Expressions.")

        self.clear(self.rt(n, 0.1))
        nxt = self.label("NEXT VIDEO", color=self.GREY, size=26).move_to(UP * 2.6)
        topic = self.title_text("FACTORS IN FACTORIAL EXPRESSIONS", color=self.YELLOW, size=44).next_to(nxt, DOWN, buff=0.3)
        teaser = self.tex("n!", "=", r"2^{?}", r"\times", r"3^{?}", r"\times", r"5^{?}", r"\times", r"\cdots", size=56,
                          colors={0: self.YELLOW, 2: self.GREEN, 4: self.BLUE, 6: self.ORANGE}).move_to(DOWN * 0.6)
        self.play(FadeIn(nxt, shift=DOWN * 0.2), FadeIn(topic, scale=1.05), run_time=self.rt(n, 0.2))
        self.shine(topic, self.YELLOW, self.rt(n, 0.1))
        self.play(Write(teaser), run_time=self.rt(n, 0.25))

        self.wait_for_narration(n)

        self.see_you_there()

        self.scene_end("done")