from manim import *
from src.animation.lms_scene import LMSScene


class EuclideanDivisionVideo(LMSScene):
    """
    Euclidean Division Method (for HCF)
    C-CAT | Section A | Module 2: Quantitative Aptitude | Day 3
    HCF & LCM > Methods of Finding HCF

    Visual concept (Euclid's own picture):
        a 48 x 18 rectangle
        -> cut off as many 18 x 18 squares as fit   (48 = 18 x 2 + 12)
        -> in the 12-wide leftover, cut 12 x 12     (18 = 12 x 1 + 6)
        -> the 6-wide leftover fills exactly with 6 x 6 squares   (12 = 6 x 2 + 0)
        the last square size, 6, tiles the whole rectangle: that is the HCF.
    Each division is one round of square-cutting; the remainder is the strip left over.

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
    YELLOW = "#FFD54A"      # the HCF
    BLUE = "#4FC3F7"        # round 1
    GREEN = "#69F0AE"       # round 2
    ORANGE = "#FFB74D"
    RED = "#FF5252"         # remainder 0 / crossed-out methods
    PURPLE = "#B388FF"
    GREY = "#8A93A6"
    GRID = "#141A26"

    STEP_COLORS = ["#4FC3F7", "#69F0AE", "#FFD54A", "#FFB74D"]
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

    def strike(self, mob, color=None):
        return Line(mob.get_left() + LEFT * 0.1, mob.get_right() + RIGHT * 0.1,
                    color=color or self.RED, stroke_width=5)

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

    def euclid_rounds(self, a, b, unit, corner):
        """
        Squares cut from an a x b rectangle, one VGroup per division round.
        corner = bottom-left point of the rectangle.
        """
        rounds = []
        x, y, w, h = corner[0], corner[1], a, b
        k = 0
        while w > 0 and h > 0:
            color = self.STEP_COLORS[k % len(self.STEP_COLORS)]
            group = VGroup()
            if w >= h:
                q, r = divmod(w, h)
                for i in range(q):
                    group.add(Square(side_length=h * unit, stroke_color=color, stroke_width=2.5,
                                     fill_color=color, fill_opacity=0.28)
                              .move_to([x + (i + 0.5) * h * unit, y + h * unit / 2, 0]))
                x += q * h * unit
                w = r
            else:
                q, r = divmod(h, w)
                for i in range(q):
                    group.add(Square(side_length=w * unit, stroke_color=color, stroke_width=2.5,
                                     fill_color=color, fill_opacity=0.28)
                              .move_to([x + w * unit / 2, y + (i + 0.5) * w * unit, 0]))
                y += q * w * unit
                h = r
            rounds.append(group)
            k += 1
        return rounds

    def division_line(self, a, b, q, r, k, size=38):
        """a = b x q + r, with the divisor and remainder coloured by round."""
        div_c = self.STEP_COLORS[k % len(self.STEP_COLORS)]
        rem_c = self.RED if r == 0 else self.STEP_COLORS[(k + 1) % len(self.STEP_COLORS)]
        return self.tex(str(a), "=", str(b), r"\times", str(q), "+", str(r), size=size,
                        colors={2: div_c, 6: rem_c})

    def outline(self, a, b, unit, corner):
        return Rectangle(width=a * unit, height=b * unit, stroke_color=self.WHITE, stroke_width=3).move_to(
            [corner[0] + a * unit / 2, corner[1] + b * unit / 2, 0])

    # =========================================================
    # 1. HOOK
    # =========================================================

    def hook(self):

        self.scene_start("hook")

        self.open_with_greeting()

        # -----------------------------------------------------
        # Narration 2 — big numbers, slow methods
        # -----------------------------------------------------

        n = self.say(
            "hook_02",
            "What if the numbers are genuinely large, and neither listing factors "
            "nor prime factorisation feels quick?",
        )

        big = self.tex(r"\text{HCF}(1071,\ 462)", "=", "?", size=60, colors={2: self.YELLOW}).move_to(UP * 2.0)
        self.play(Write(big), run_time=self.rt(n, 0.2))

        listing = self.label("listing factors", color=self.GREY, size=34).move_to([-3.2, 0.0, 0])
        primes = self.label("prime factorisation", color=self.GREY, size=34).move_to([3.2, 0.0, 0])
        self.play(FadeIn(listing, shift=UP * 0.2), FadeIn(primes, shift=UP * 0.2), run_time=self.rt(n, 0.15))
        slow_l = self.label("slow...", color=self.RED, size=24).next_to(listing, DOWN, buff=0.25)
        slow_p = self.label("slow...", color=self.RED, size=24).next_to(primes, DOWN, buff=0.25)
        self.play(Create(self.strike(listing)), Create(self.strike(primes)), FadeIn(slow_l, slow_p),
                  run_time=self.rt(n, 0.15))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — nothing but repeated division
        # -----------------------------------------------------

        n = self.say(
            "hook_03",
            "There's an elegant, almost magical method, using nothing but repeated division. Let's meet it today.",
        )

        self.clear(self.rt(n, 0.12), keep=[big])
        div = MathTex(r"\div", font_size=110, color=self.YELLOW).move_to(DOWN * 0.8)
        loop = Arc(radius=1.3, start_angle=PI / 2, angle=-1.7 * PI, color=self.BLUE, stroke_width=5,
                   arc_center=div.get_center()).add_tip(tip_length=0.25)
        self.play(FadeIn(div, scale=0.5), run_time=self.rt(n, 0.12))
        self.play(Create(loop), run_time=self.rt(n, 0.2))
        self.play(Rotate(loop, angle=-TAU, about_point=div.get_center()), Flash(div, color=self.YELLOW,
                                                                                 flash_radius=0.9),
                  run_time=self.rt(n, 0.25))
        self.shine(div, self.YELLOW, self.rt(n, 0.08))

        self.wait_for_narration(n)

    # =========================================================
    # 2. INTRODUCTION
    # =========================================================

    def introduction(self):

        self.scene_start("introduction")

        n = self.say(
            "intro_01",
            "Welcome back! Today we meet the Euclidean Division Method — the fastest, most elegant approach of all.",
        )

        self.clear(self.rt(n, 0.12))
        title = self.title_text("EUCLIDEAN DIVISION METHOD", color=self.YELLOW, size=54).move_to(UP * 0.6)
        sub = self.label("the fastest, most elegant HCF method", color=self.GREY, size=28).next_to(title, DOWN, buff=0.4)
        self.play(FadeIn(title, scale=1.1), run_time=self.rt(n, 0.2))
        self.shine(title, self.YELLOW, self.rt(n, 0.12))
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=self.rt(n, 0.15))
        self.sweep(title, self.YELLOW, self.rt(n, 0.15))

        self.wait_for_narration(n)

    # =========================================================
    # 3. HOW — the general recipe
    # =========================================================

    def how(self):

        self.scene_start("how")

        # -----------------------------------------------------
        # Narration 1
        # -----------------------------------------------------

        n = self.say("how_01", "So how does this method work?")

        self.clear(self.rt(n, 0.3))
        head = self.label("THE RECIPE", color=self.GREY, size=26, weight=BOLD).to_corner(UL, buff=0.5)
        self.play(FadeIn(head), run_time=self.rt(n, 0.2))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — divide larger by smaller, keep the remainder
        # -----------------------------------------------------

        n = self.say("how_02", "My dear students, divide the larger number by the smaller, note the remainder,")

        c1, c2, c3 = self.STEP_COLORS[0], self.STEP_COLORS[1], self.STEP_COLORS[2]
        row1 = self.tex("a", "=", "b", r"\times", "q_1", "+", "r_1", size=52,
                        colors={2: c1, 6: c2}).move_to([0, 2.0, 0])
        self.play(Write(row1[0:5]), run_time=self.rt(n, 0.25))
        self.play(Write(row1[5:]), run_time=self.rt(n, 0.15))
        rem_lbl = self.label("remainder", color=c2, size=22).next_to(row1[6], RIGHT, buff=0.35)
        self.play(FadeIn(rem_lbl, shift=LEFT * 0.1), Indicate(row1[6], color=c2), run_time=self.rt(n, 0.15))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — divisor and remainder shift one place left, repeatedly
        # -----------------------------------------------------

        n = self.say(
            "how_03",
            "then repeat — dividing the previous divisor by that remainder — again and again, "
            "until the remainder finally becomes 0.",
        )

        row2 = self.tex("b", "=", "r_1", r"\times", "q_2", "+", "r_2", size=52,
                        colors={0: c1, 2: c2, 6: c3}).move_to([0, 0.5, 0])
        row3 = self.tex("r_1", "=", "r_2", r"\times", "q_3", "+", "0", size=52,
                        colors={0: c2, 2: c3, 6: self.RED}).move_to([0, -1.0, 0])
        # the baton pass: yesterday's divisor becomes today's dividend,
        # yesterday's remainder becomes today's divisor
        self.play(TransformFromCopy(row1[2], row2[0]), TransformFromCopy(row1[6], row2[2]),
                  FadeOut(rem_lbl), run_time=self.rt(n, 0.2))
        self.play(FadeIn(row2[1]), FadeIn(row2[3:]), run_time=self.rt(n, 0.12))
        self.play(TransformFromCopy(row2[0 + 2], row3[0]), TransformFromCopy(row2[6], row3[2]),
                  run_time=self.rt(n, 0.2))
        self.play(FadeIn(row3[1]), FadeIn(row3[3:6]), run_time=self.rt(n, 0.1))
        self.play(FadeIn(row3[6], scale=1.6), Flash(row3[6], color=self.RED, flash_radius=0.4),
                  run_time=self.rt(n, 0.12))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 4 — the answer is the last non-zero divisor
        # -----------------------------------------------------

        n = self.say("how_04", "Your HCF is the very last non-zero divisor.")

        box = SurroundingRectangle(row3[2], color=self.YELLOW, buff=0.12, corner_radius=0.08)
        answer = self.tex(r"\text{HCF}", "=", "r_2", size=56, colors={0: self.YELLOW, 2: c3}).move_to([0, -2.6, 0])
        self.play(Create(box), run_time=self.rt(n, 0.2))
        self.play(TransformFromCopy(row3[2], answer[2]), FadeIn(answer[0:2]), run_time=self.rt(n, 0.25))
        self.shine(answer, self.YELLOW, self.rt(n, 0.15))

        self.wait_for_narration(n)

    # =========================================================
    # 4. WHAT — 48 and 18, cut into squares
    # =========================================================

    def what(self):

        self.scene_start("what")

        unit, corner = 0.16, np.array([-6.5, -0.9, 0])
        rect = self.outline(48, 18, unit, corner)
        rounds = self.euclid_rounds(48, 18, unit, corner)
        w_brace = Brace(rect, DOWN, buff=0.1, color=self.GREY)
        w_lbl = MathTex("48", font_size=34, color=self.GREY).next_to(w_brace, DOWN, buff=0.08)
        h_brace = Brace(rect, LEFT, buff=0.1, color=self.GREY)
        h_lbl = MathTex("18", font_size=34, color=self.GREY).next_to(h_brace, LEFT, buff=0.08)
        steps = [(48, 18, 2, 12), (18, 12, 1, 6), (12, 6, 2, 0)]
        lines = VGroup(*[self.division_line(a, b, q, r, k) for k, (a, b, q, r) in enumerate(steps)])
        lines.arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to([4.4, 0.55, 0])

        texts = [
            "For 48 and 18: divide 48 by 18, giving quotient 2 and remainder 12.",
            "Now divide 18 by 12, giving quotient 1 and remainder 6.",
            "Now divide 12 by 6, giving quotient 2 and remainder 0.",
        ]

        for k, text in enumerate(texts):
            n = self.say(f"what_0{k + 1}", text)
            if k == 0:
                self.clear(self.rt(n, 0.08))
                self.play(Create(rect), GrowFromCenter(w_brace), GrowFromCenter(h_brace), FadeIn(w_lbl, h_lbl),
                          run_time=self.rt(n, 0.15))
            self.play(Write(lines[k]), run_time=self.rt(n, 0.25))
            # one round of cutting = one division
            self.play(LaggedStart(*[DrawBorderThenFill(s) for s in rounds[k]], lag_ratio=0.35),
                      run_time=self.rt(n, 0.25))
            if steps[k][3] == 0:
                done = VGroup(self.check_mark(self.GREEN), self.label("nothing left over", color=self.GREEN, size=22))
                done.arrange(RIGHT, buff=0.15).next_to(rect, UP, buff=0.3)
                self.play(FadeIn(done, shift=DOWN * 0.1), run_time=self.rt(n, 0.12))
            self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 4 — 6 is the HCF: its square tiles everything
        # -----------------------------------------------------

        n = self.say("what_04", "Since we've reached remainder 0, our HCF is the last divisor used — 6.")

        box = SurroundingRectangle(lines[2][2], color=self.YELLOW, buff=0.1, corner_radius=0.06)
        self.play(Create(box), run_time=self.rt(n, 0.1))
        answer = self.tex(r"\text{HCF}", "=", "6", size=60, colors={0: self.YELLOW, 2: self.YELLOW})
        answer.move_to([4.4, -1.9, 0])
        self.play(TransformFromCopy(lines[2][2], answer[2]), FadeIn(answer[0:2]), run_time=self.rt(n, 0.2))
        self.shine(answer, self.YELLOW, self.rt(n, 0.08))

        # a 6 x 6 grid covers the whole 48 x 18 rectangle: 6 divides both
        s = 6 * unit
        grid = VGroup(*[Square(side_length=s, stroke_color=self.YELLOW, stroke_width=1.5)
                        .move_to([corner[0] + (i + 0.5) * s, corner[1] + (j + 0.5) * s, 0])
                        for i in range(8) for j in range(3)])
        self.play(LaggedStart(*[Create(g) for g in grid], lag_ratio=0.03), run_time=self.rt(n, 0.3))
        self.sweep(rect, self.YELLOW, self.rt(n, 0.1), buff=0.08)

        self.wait_for_narration(n)

    # =========================================================
    # 5. WHY
    # =========================================================

    def why(self):

        self.scene_start("why")

        n = self.say("why_01", "Now, why does this matter?")

        self.clear(self.rt(n, 0.25))
        big = self.tex(r"\text{HCF}(1071,\ 462)", size=52, colors={0: self.WHITE}).move_to(UP * 2.9)
        self.play(FadeIn(big, shift=DOWN * 0.2), run_time=self.rt(n, 0.3))

        self.wait_for_narration(n)

        n = self.say(
            "why_02",
            "Because this method works beautifully even for enormous numbers, needing only a handful of "
            "quick divisions, with no factorisation or listing required at all.",
        )

        steps = [(1071, 462, 2, 147), (462, 147, 3, 21), (147, 21, 7, 0)]
        lines = VGroup(*[self.division_line(a, b, q, r, k, size=42) for k, (a, b, q, r) in enumerate(steps)])
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT).move_to([-1.2, 0.6, 0])
        counters = VGroup(*[
            VGroup(Circle(radius=0.28, color=self.YELLOW, fill_color=self.YELLOW, fill_opacity=1),
                   Text(str(i + 1), font_size=24, color=self.BG, weight=BOLD))
            for i in range(3)
        ])
        for c, line in zip(counters, lines):
            c[1].move_to(c[0])
            c.next_to(line, LEFT, buff=0.4)

        for c, line in zip(counters, lines):
            self.play(FadeIn(c, scale=0.5), Write(line), run_time=self.rt(n, 0.13))
        answer = self.tex(r"\text{HCF}", "=", "21", size=54, colors={0: self.YELLOW, 2: self.YELLOW})
        answer.next_to(lines, DOWN, buff=0.55)
        self.play(TransformFromCopy(lines[2][2], answer[2]), FadeIn(answer[0:2]), run_time=self.rt(n, 0.12))
        self.shine(answer, self.YELLOW, self.rt(n, 0.06))

        not_needed = VGroup(self.label("no factor lists", color=self.GREY, size=26),
                            self.label("no factor trees", color=self.GREY, size=26)).arrange(DOWN, buff=0.35)
        not_needed.move_to([4.9, 0.6, 0])
        strikes = VGroup(*[self.strike(t) for t in not_needed])
        self.play(FadeIn(not_needed), run_time=self.rt(n, 0.08))
        self.play(Create(strikes), run_time=self.rt(n, 0.08))
        only = self.label("just 3 divisions", color=self.GREEN, size=28, weight=BOLD).next_to(not_needed, DOWN, buff=0.5)
        self.play(FadeIn(only, shift=UP * 0.1), run_time=self.rt(n, 0.08))

        self.wait_for_narration(n)

    # =========================================================
    # 6. REAL WORLD EXAMPLE — 252 and 105
    # =========================================================

    def real_world_example(self):

        self.scene_start("real_world")

        unit, corner = 0.025, np.array([-4.9, -0.3, 0])
        rect = self.outline(252, 105, unit, corner)
        rounds = self.euclid_rounds(252, 105, unit, corner)
        steps = [(252, 105, 2, 42), (105, 42, 2, 21), (42, 21, 2, 0)]
        lines = VGroup(*[self.division_line(a, b, q, r, k, size=36) for k, (a, b, q, r) in enumerate(steps)])
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT).move_to([4.5, 1.0, 0])

        # -----------------------------------------------------
        # Narration 1
        # -----------------------------------------------------

        n = self.say(
            "example_01",
            "Let me tell you about a boy named Aaryaman, finding the HCF of 252 and 105 using this method.",
        )

        aaryaman = self.person(self.PURPLE).scale(0.55).move_to([-6.1, -2.4, 0])
        name = self.label("Aaryaman", color=self.YELLOW, size=22).next_to(aaryaman, RIGHT, buff=0.2)
        question = self.tex(r"\text{HCF}(252,\ 105)", size=44).move_to([4.5, 3.0, 0])
        self.slide_board(VGroup(aaryaman, name), LEFT, self.rt(n, 0.2))
        self.play(Write(question), run_time=self.rt(n, 0.2))
        self.play(Create(rect), run_time=self.rt(n, 0.15))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — three rounds
        # -----------------------------------------------------

        n = self.say(
            "example_02",
            "He divided 252 by 105, getting remainder 42. Then 105 by 42, getting remainder 21. "
            "Then 42 by 21, getting remainder 0.",
        )

        for k in range(3):
            self.play(Write(lines[k]), LaggedStart(*[DrawBorderThenFill(s) for s in rounds[k]], lag_ratio=0.3),
                      run_time=self.rt(n, 0.25))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — the answer, in three steps
        # -----------------------------------------------------

        n = self.say(
            "example_03",
            "His HCF, the last divisor, was 21 — found in just three quick steps, "
            "without ever listing a single factor.",
        )

        box = SurroundingRectangle(lines[2][2], color=self.YELLOW, buff=0.1, corner_radius=0.06)
        answer = self.tex(r"\text{HCF}", "=", "21", size=56, colors={0: self.YELLOW, 2: self.YELLOW})
        answer.move_to([4.5, -1.3, 0])
        self.play(Create(box), run_time=self.rt(n, 0.1))
        self.play(TransformFromCopy(lines[2][2], answer[2]), FadeIn(answer[0:2]), run_time=self.rt(n, 0.18))
        self.shine(answer, self.YELLOW, self.rt(n, 0.08))
        three = self.label("3 quick steps", color=self.GREEN, size=28, weight=BOLD).next_to(answer, DOWN, buff=0.4)
        self.play(FadeIn(three, shift=UP * 0.1), run_time=self.rt(n, 0.1))
        self.play(LaggedStart(*[Indicate(r, color=self.YELLOW, scale_factor=1.05) for r in rounds], lag_ratio=0.3),
                  run_time=self.rt(n, 0.2))

        self.wait_for_narration(n)

    # =========================================================
    # 7. SUMMARY — the loop
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
            "Divide repeatedly, larger by smaller, using each remainder as the next divisor, "
            "until you reach 0 — the last divisor used is your HCF.",
        )

        def node(text, color, width):
            box = RoundedRectangle(corner_radius=0.2, width=width, height=1.2, stroke_color=color, stroke_width=3,
                                   fill_color=color, fill_opacity=0.12)
            return VGroup(box, self.label(text, color=color, size=24, weight=BOLD).move_to(box))

        divide = node("divide larger\nby smaller", self.BLUE, 3.4).move_to([-4.2, -0.2, 0])
        shift = node("remainder becomes\nnext divisor", self.GREEN, 3.6).move_to([0.2, -0.2, 0])
        finish = node("last divisor\n= HCF", self.YELLOW, 2.8).move_to([4.8, -0.2, 0])

        top_p1, top_p2 = divide.get_top() + RIGHT * 0.8, shift.get_top() + LEFT * 0.8
        mid = (top_p1 + top_p2) / 2
        forward = Arc(radius=np.linalg.norm(top_p2 - top_p1) / 2, start_angle=PI, angle=-PI, arc_center=mid,
                      color=self.WHITE, stroke_width=4).stretch(0.6, 1, about_point=mid).add_tip(tip_length=0.2)
        bot_p1, bot_p2 = shift.get_bottom() + LEFT * 0.8, divide.get_bottom() + RIGHT * 0.8
        mid_b = (bot_p1 + bot_p2) / 2
        back = Arc(radius=np.linalg.norm(bot_p2 - bot_p1) / 2, start_angle=0, angle=-PI, arc_center=mid_b,
                   color=self.WHITE, stroke_width=4).stretch(0.6, 1, about_point=mid_b).add_tip(tip_length=0.2)
        again = self.label("repeat", color=self.GREY, size=22).next_to(back, DOWN, buff=0.1)
        exit_arrow = Arrow(shift.get_right(), finish.get_left(), buff=0.12, color=self.RED, stroke_width=5)
        exit_lbl = MathTex(r"r = 0", font_size=32, color=self.RED).next_to(exit_arrow, UP, buff=0.1)

        self.play(FadeIn(divide, shift=UP * 0.2), run_time=self.rt(n, 0.1))
        self.play(Create(forward), FadeIn(shift, shift=UP * 0.2), run_time=self.rt(n, 0.15))
        self.play(Create(back), FadeIn(again), run_time=self.rt(n, 0.12))
        self.play(ShowPassingFlash(VGroup(forward, back).copy().set_stroke(self.YELLOW, 8), time_width=0.5),
                  run_time=self.rt(n, 0.12))
        self.play(GrowArrow(exit_arrow), FadeIn(exit_lbl), run_time=self.rt(n, 0.1))
        self.play(FadeIn(finish, scale=0.9), run_time=self.rt(n, 0.1))
        self.shine(finish[0], self.YELLOW, self.rt(n, 0.08))

        self.wait_for_narration(n)

    # =========================================================
    # 8. DONE
    # =========================================================

    def done(self):

        self.scene_start("done")

        n = self.say("done_01", "That's the Euclidean Division Method for you — our HCF toolkit, now complete.")

        self.clear(self.rt(n, 0.12))
        kit = RoundedRectangle(corner_radius=0.2, width=9.0, height=3.0, stroke_color=self.GREY, stroke_width=3)
        kit.move_to(DOWN * 0.3)
        kit_lbl = self.label("HCF TOOLKIT", color=self.GREY, size=24, weight=BOLD).next_to(kit, UP, buff=0.2)
        tools = VGroup(*[
            VGroup(self.check_mark(self.GREEN), self.label(t, color=c, size=28, weight=BOLD)).arrange(RIGHT, buff=0.2)
            for t, c in [("Factor Method", self.WHITE), ("Prime Factorisation", self.WHITE),
                         ("Euclidean Division", self.YELLOW)]
        ]).arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(kit)
        self.play(Create(kit), FadeIn(kit_lbl), run_time=self.rt(n, 0.15))
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.2) for t in tools], lag_ratio=0.3), run_time=self.rt(n, 0.3))
        self.shine(tools[2], self.YELLOW, self.rt(n, 0.1))

        self.wait_for_narration(n)

        n = self.say("done_02", "In our next video, we shift focus to LCM — Methods of Finding LCM.")

        self.clear(self.rt(n, 0.12))
        nxt = self.label("NEXT VIDEO", color=self.GREY, size=26).move_to(UP * 1.8)
        topic = self.title_text("METHODS OF FINDING LCM", color=self.YELLOW, size=54).next_to(nxt, DOWN, buff=0.3)
        self.play(FadeIn(nxt, shift=DOWN * 0.2), FadeIn(topic, scale=1.1), run_time=self.rt(n, 0.3))
        self.shine(topic, self.YELLOW, self.rt(n, 0.15))

        self.wait_for_narration(n)

        self.see_you_there()

        self.scene_end("done")