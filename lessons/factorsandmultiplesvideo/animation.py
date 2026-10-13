from manim import *
from src.animation.lms_scene import LMSScene


class FactorsAndMultiplesVideo(LMSScene):
    """
    Factors and Multiples
    C-CAT | Section A | Module 2: Quantitative Aptitude | Day 3
    HCF & LCM > Fundamentals of HCF & LCM

    Visual concept:
        FACTOR   = 12 dots split into equal groups with nothing left over  (divides IN)
        MULTIPLE = hops of 12 along a number line: 12, 24, 36, 48, ...     (multiplies OUT)
        factors -> build HCF,  multiples -> build LCM

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
    YELLOW = "#FFD54A"      # the number itself
    GREEN = "#69F0AE"       # factors
    BLUE = "#4FC3F7"        # multiples
    RED = "#FF5252"         # leftovers
    ORANGE = "#FFB74D"
    PURPLE = "#B388FF"
    GREY = "#8A93A6"
    GRID = "#141A26"

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
        """Old board slides out, new board slides in: feels like a camera pan."""
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

    def block(self, text, color, width=2.5, height=1.0):
        box = RoundedRectangle(corner_radius=0.12, width=width, height=height, stroke_color=color,
                               stroke_width=3, fill_color=color, fill_opacity=0.2)
        return VGroup(box, self.label(text, color=color, size=28, weight=BOLD).move_to(box))

    def badge(self, value, color=None, radius=0.6, size=48):
        c = color or self.YELLOW
        ring = Circle(radius=radius, stroke_color=c, stroke_width=4, fill_color=c, fill_opacity=0.15)
        return VGroup(ring, MathTex(str(value), font_size=size, color=c).move_to(ring))

    def dot_array(self, rows, cols, color, spacing=0.19, radius=0.065):
        dots = VGroup(*[Dot(radius=radius, color=color) for _ in range(rows * cols)])
        return dots.arrange_in_grid(rows=rows, cols=cols, buff=spacing - 2 * radius)

    def group_positions(self, count, size, center, spacing=0.3, gap=0.55):
        """x-positions for `count` dots split into groups of `size` (leftovers form a last group)."""
        xs = [i * spacing + (i // size) * gap for i in range(count)]
        mid = (xs[0] + xs[-1]) / 2
        full = (count // size) * size
        return [(np.array([center[0] + x - mid, center[1], 0]), i >= full) for i, x in enumerate(xs)]

    def regroup(self, dots, size, center, ok_color):
        return [d.animate.move_to(p).set_color(self.RED if left else ok_color)
                for d, (p, left) in zip(dots, self.group_positions(len(dots), size, center))]

    def number_line(self, top, length, y, x_center=0.0):
        nl = NumberLine(x_range=[0, top, top / 10 if top % 10 == 0 else 1], length=length,
                        color=self.GREY, stroke_width=3, include_numbers=False, tick_size=0.06)
        return nl.move_to([x_center, y, 0])

    def hop(self, p1, p2, color, height_ratio=0.55):
        """Upper arc from p1 to p2 with an arrow tip: one jump of a multiple."""
        mid = (p1 + p2) / 2
        r = np.linalg.norm(p2 - p1) / 2
        arc = Arc(radius=r, start_angle=PI, angle=-PI, arc_center=mid, color=color, stroke_width=4)
        arc.stretch(height_ratio, 1, about_point=mid)
        arc.add_tip(tip_length=0.18)
        return arc

    # =========================================================
    # 1. HOOK
    # =========================================================

    def hook(self):

        self.scene_start("hook")

        self.open_with_greeting()

        # -----------------------------------------------------
        # Narration 2
        # -----------------------------------------------------

        n = self.say("hook_02", "Do you remember factors and multiples from our Number Systems journey?")

        factors = self.title_text("FACTORS", color=self.GREEN, size=56).move_to([-3.2, 0.8, 0])
        multiples = self.title_text("MULTIPLES", color=self.BLUE, size=56).move_to([3.2, 0.8, 0])
        recall = self.label("from our Number Systems journey", color=self.GREY, size=26).move_to(DOWN * 0.4)

        self.play(FadeIn(factors, shift=RIGHT * 0.3), run_time=self.rt(n, 0.2))
        self.play(FadeIn(multiples, shift=LEFT * 0.3), run_time=self.rt(n, 0.2))
        self.play(FadeIn(recall), run_time=self.rt(n, 0.15))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — two foundation blocks, something new above
        # -----------------------------------------------------

        n = self.say("hook_03", "A quick refresh, and we'll be ready to build something new on top of them.")

        self.block_f = self.block("factors", self.GREEN).move_to([-1.3, -2.4, 0])
        self.block_m = self.block("multiples", self.BLUE).move_to([1.3, -2.4, 0])
        self.play(ReplacementTransform(factors, self.block_f), ReplacementTransform(multiples, self.block_m),
                  FadeOut(recall), run_time=self.rt(n, 0.3))

        house = DashedVMobject(Polygon([-2.55, -1.85, 0], [-2.55, 0.4, 0], [0, 1.8, 0], [2.55, 0.4, 0],
                                       [2.55, -1.85, 0], stroke_color=self.GREY, stroke_width=3), num_dashes=60)
        q = Text("?", font_size=90, color=self.YELLOW, weight=BOLD).move_to([0, -0.4, 0])
        self.house = VGroup(house, q)
        self.play(Create(house), Write(q), run_time=self.rt(n, 0.3))
        self.shine(q, self.YELLOW, self.rt(n, 0.1))

        self.wait_for_narration(n)

    # =========================================================
    # 2. INTRODUCTION
    # =========================================================

    def introduction(self):

        self.scene_start("introduction")

        n = self.say(
            "intro_01",
            "Welcome back! Today's quick refresher — Factors and Multiples — "
            "the two building blocks behind HCF and LCM.",
        )

        title = self.title_text("FACTORS & MULTIPLES", color=self.YELLOW, size=56).move_to(UP * 2.9)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=self.rt(n, 0.15))
        self.shine(title, self.YELLOW, self.rt(n, 0.1))

        # the "something new" turns out to be HCF and LCM, standing on the two blocks
        hcf = self.block("HCF", self.GREEN).next_to(self.block_f, UP, buff=0.12)
        lcm = self.block("LCM", self.BLUE).next_to(self.block_m, UP, buff=0.12)
        self.play(FadeOut(self.house), run_time=self.rt(n, 0.1))
        self.play(FadeIn(hcf, shift=DOWN * 0.5), FadeIn(lcm, shift=DOWN * 0.5), run_time=self.rt(n, 0.2))
        self.sweep(VGroup(self.block_f, self.block_m), self.YELLOW, self.rt(n, 0.15))

        self.wait_for_narration(n)

    # =========================================================
    # 3. HOW
    # =========================================================

    def how(self):

        self.scene_start("how")

        # -----------------------------------------------------
        # Narration 1
        # -----------------------------------------------------

        n = self.say("how_01", "So how do we tell them apart?")

        self.clear(self.rt(n, 0.25))
        self.twelve = self.badge(12).move_to([0, 3.0, 0])
        self.play(FadeIn(self.twelve, scale=0.8), run_time=self.rt(n, 0.3))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — a factor divides in with nothing left over
        # -----------------------------------------------------

        n = self.say("how_02", "My dear students, a factor divides neatly into a number,")

        self.dots = VGroup(*[Dot(radius=0.12, color=self.YELLOW) for _ in range(12)]).arrange(RIGHT, buff=0.26)
        self.dots.move_to([0, 1.6, 0])
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in self.dots], lag_ratio=0.08),
                  run_time=self.rt(n, 0.15))

        # groups of 5 don't fit: 2 dots left over
        self.play(*self.regroup(self.dots, 5, [0, 1.6, 0], self.GREY), run_time=self.rt(n, 0.15))
        bad = self.tex(r"12 \div 5", r"\;\rightarrow\;", r"\text{2 left over}", size=36,
                       colors={2: self.RED}).move_to([0, 0.75, 0])
        self.play(FadeIn(bad, shift=UP * 0.1), run_time=self.rt(n, 0.1))

        # groups of 4 fit exactly
        good = self.tex(r"12 \div 4 = 3", r"\;\text{exactly}", size=36, colors={1: self.GREEN}).move_to(bad)
        self.play(*self.regroup(self.dots, 4, [0, 1.6, 0], self.GREEN), FadeOut(bad), run_time=self.rt(n, 0.15))
        self.play(FadeIn(good, shift=UP * 0.1), run_time=self.rt(n, 0.1))
        self.factor_note = good
        self.shine(good, self.GREEN, self.rt(n, 0.08))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — a multiple is reached by multiplying upward
        # -----------------------------------------------------

        n = self.say("how_03", "while a multiple is what you get by multiplying a number upward.")

        self.line = self.number_line(60, 11.5, -1.9)
        self.play(Create(self.line), run_time=self.rt(n, 0.15))
        self.hops = VGroup()
        self.mult_labels = VGroup()
        for k in (1, 2):
            p1, p2 = self.line.n2p(12 * (k - 1)), self.line.n2p(12 * k)
            arc = self.hop(p1, p2, self.BLUE)
            lbl = MathTex(str(12 * k), font_size=34, color=self.BLUE).next_to(p2, DOWN, buff=0.25)
            times = MathTex(rf"\times {k}", font_size=28, color=self.GREY).next_to(arc, UP, buff=0.08)
            self.play(Create(arc), FadeIn(lbl), FadeIn(times), run_time=self.rt(n, 0.17))
            self.hops.add(VGroup(arc, times))
            self.mult_labels.add(lbl)
        zero = MathTex("0", font_size=30, color=self.GREY).next_to(self.line.n2p(0), DOWN, buff=0.25)
        self.play(FadeIn(zero), run_time=self.rt(n, 0.06))
        self.zero_lbl = zero

        self.wait_for_narration(n)

    # =========================================================
    # 4. WHAT
    # =========================================================

    def what(self):

        self.scene_start("what")

        # -----------------------------------------------------
        # Narration 1 — every way 12 splits into equal rows
        # -----------------------------------------------------

        n = self.say("what_01", "The factors of 12 are 1, 2, 3, 4, 6, and 12 — each divides in exactly.")

        self.play(FadeOut(self.dots, self.factor_note, self.twelve), run_time=self.rt(n, 0.08))

        heading = self.label("FACTORS OF 12", color=self.GREEN, size=26, weight=BOLD).move_to([-5.3, 3.3, 0])
        pairs = [(1, 12), (2, 6), (3, 4), (4, 3), (6, 2), (12, 1)]
        arrays = VGroup(*[self.dot_array(r, c, self.GREEN) for r, c in pairs])
        arrays.arrange(RIGHT, buff=0.55, aligned_edge=DOWN).move_to([0.4, 1.35, 0])
        tags = VGroup(*[MathTex(str(r), font_size=40, color=self.GREEN).move_to([a.get_x(), -0.1, 0])
                        for (r, _), a in zip(pairs, arrays)])

        self.play(FadeIn(heading), run_time=self.rt(n, 0.07))
        self.play(LaggedStart(*[FadeIn(a, scale=0.6) for a in arrays], lag_ratio=0.2), run_time=self.rt(n, 0.3))
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.15) for t in tags], lag_ratio=0.15), run_time=self.rt(n, 0.15))
        self.sweep(VGroup(arrays, tags), self.GREEN, self.rt(n, 0.12))
        self.factor_board = VGroup(heading, arrays, tags)

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — the hops keep going, forever
        # -----------------------------------------------------

        n = self.say(
            "what_02",
            "The multiples of 12 are 12, 24, 36, 48, and onward, forever — "
            "each comes from multiplying 12 upward.",
        )

        m_heading = self.label("MULTIPLES OF 12", color=self.BLUE, size=26, weight=BOLD).move_to([-5.1, -0.9, 0])
        self.play(FadeIn(m_heading), run_time=self.rt(n, 0.07))
        for k in (3, 4):
            p1, p2 = self.line.n2p(12 * (k - 1)), self.line.n2p(12 * k)
            arc = self.hop(p1, p2, self.BLUE)
            lbl = MathTex(str(12 * k), font_size=34, color=self.BLUE).next_to(p2, DOWN, buff=0.25)
            times = MathTex(rf"\times {k}", font_size=28, color=self.GREY).next_to(arc, UP, buff=0.08)
            self.play(Create(arc), FadeIn(lbl), FadeIn(times), run_time=self.rt(n, 0.13))
            self.hops.add(VGroup(arc, times))
            self.mult_labels.add(lbl)

        onward = Arrow(self.line.n2p(50), self.line.n2p(60) + RIGHT * 0.5, buff=0, color=self.BLUE, stroke_width=5)
        forever = self.label("forever", color=self.BLUE, size=24, weight=BOLD).next_to(onward, UP, buff=0.1)
        self.play(GrowArrow(onward), FadeIn(forever), run_time=self.rt(n, 0.12))
        self.play(LaggedStart(*[Indicate(l, color=self.BLUE) for l in self.mult_labels], lag_ratio=0.2),
                  run_time=self.rt(n, 0.15))
        self.shine(forever, self.BLUE, self.rt(n, 0.06))

        self.wait_for_narration(n)

    # =========================================================
    # 5. WHY
    # =========================================================

    def why(self):

        self.scene_start("why")

        # -----------------------------------------------------
        # Narration 1
        # -----------------------------------------------------

        n = self.say("why_01", "Now, why does this matter?")

        self.clear(self.rt(n, 0.25))
        hcf = self.block("HCF", self.GREEN, width=3.0, height=1.1).move_to([-3.3, 2.1, 0])
        lcm = self.block("LCM", self.BLUE, width=3.0, height=1.1).move_to([3.3, 2.1, 0])
        self.play(FadeIn(hcf, shift=DOWN * 0.2), FadeIn(lcm, shift=DOWN * 0.2), run_time=self.rt(n, 0.3))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — each is built from one of the two ideas
        # -----------------------------------------------------

        n = self.say(
            "why_02",
            "Because HCF is built entirely from factors, and LCM is built entirely from multiples —",
        )

        f_chips = VGroup(*[self.badge(v, self.GREEN, radius=0.36, size=30) for v in [1, 2, 3, 4, 6, 12]])
        f_chips.arrange(RIGHT, buff=0.12).move_to([-3.3, -0.3, 0])
        m_chips = VGroup(*[self.badge(v, self.BLUE, radius=0.36, size=28) for v in [12, 24, 36, 48]])
        m_chips.add(MathTex(r"\cdots", color=self.BLUE))
        m_chips.arrange(RIGHT, buff=0.12).move_to([3.3, -0.3, 0])
        up_f = Arrow(f_chips.get_top(), hcf.get_bottom(), buff=0.15, color=self.GREEN, stroke_width=5)
        up_m = Arrow(m_chips.get_top(), lcm.get_bottom(), buff=0.15, color=self.BLUE, stroke_width=5)
        cap_f = self.label("built from factors", color=self.GREEN, size=24).next_to(f_chips, DOWN, buff=0.3)
        cap_m = self.label("built from multiples", color=self.BLUE, size=24).next_to(m_chips, DOWN, buff=0.3)

        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in f_chips], lag_ratio=0.1), run_time=self.rt(n, 0.18))
        self.play(GrowArrow(up_f), FadeIn(cap_f), run_time=self.rt(n, 0.12))
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in m_chips], lag_ratio=0.1), run_time=self.rt(n, 0.18))
        self.play(GrowArrow(up_m), FadeIn(cap_m), run_time=self.rt(n, 0.12))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — the rest of the topic sits on top
        # -----------------------------------------------------

        n = self.say("why_03", "get comfortable with both, and the rest of this topic falls into place naturally.")

        roof = Polygon([-5.2, 2.85, 0], [0, 3.75, 0], [5.2, 2.85, 0], stroke_color=self.YELLOW, stroke_width=4,
                       fill_color=self.YELLOW, fill_opacity=0.15)
        roof_lbl = self.label("HCF & LCM", color=self.YELLOW, size=24, weight=BOLD).move_to([0, 3.2, 0])
        self.play(FadeIn(VGroup(roof, roof_lbl), shift=DOWN * 0.6), run_time=self.rt(n, 0.25))
        self.play(Indicate(hcf, color=self.GREEN), Indicate(lcm, color=self.BLUE), run_time=self.rt(n, 0.2))
        self.shine(roof_lbl, self.YELLOW, self.rt(n, 0.1))

        self.wait_for_narration(n)

    # =========================================================
    # 6. REAL WORLD EXAMPLE
    # =========================================================

    def real_world_example(self):

        self.scene_start("real_world")

        # -----------------------------------------------------
        # Narration 1 — 4 is a factor of 20
        # -----------------------------------------------------

        n = self.say(
            "example_01",
            "Let me tell you about a girl named Anushka, reminding her younger brother that "
            "4 is a factor of 20, since it divides in exactly,",
        )

        anushka = self.person(self.PURPLE).scale(0.6).move_to([-6.0, 0.4, 0])
        brother = self.person(self.ORANGE).scale(0.42)
        brother.next_to(anushka, RIGHT, buff=0.3).align_to(anushka, DOWN)
        name = self.label("Anushka", color=self.YELLOW, size=24).next_to(anushka, DOWN, buff=0.2)
        twenty = self.badge(20).move_to([1.2, 2.9, 0])

        self.slide_board(VGroup(anushka, brother, name), LEFT, self.rt(n, 0.15))
        self.play(FadeIn(twenty, scale=0.8), run_time=self.rt(n, 0.08))

        dots = VGroup(*[Dot(radius=0.1, color=self.YELLOW) for _ in range(20)]).arrange(RIGHT, buff=0.12)
        dots.move_to([1.2, 1.7, 0])
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.04), run_time=self.rt(n, 0.12))
        self.play(*self.regroup(dots, 4, [1.2, 1.7, 0], self.GREEN), run_time=self.rt(n, 0.15))
        fact = self.tex(r"20 \div 4 = 5", r"\;\Rightarrow\;", r"4 \text{ is a factor of } 20",
                        size=36, colors={2: self.GREEN}).move_to([1.2, 0.7, 0])
        self.play(FadeIn(fact, shift=UP * 0.1), run_time=self.rt(n, 0.12))
        self.shine(fact[2], self.GREEN, self.rt(n, 0.06))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — 40 is a multiple of 20
        # -----------------------------------------------------

        n = self.say("example_02", "while 40 is a multiple of 20, since it comes from multiplying 20 by 2.")

        line = NumberLine(x_range=[0, 45, 5], length=8.4, color=self.GREY, stroke_width=3,
                          include_numbers=False, tick_size=0.06).move_to([1.8, -1.6, 0])
        self.play(Create(line), run_time=self.rt(n, 0.12))
        marks = VGroup(*[MathTex(str(v), font_size=30, color=self.BLUE if v else self.GREY)
                         .next_to(line.n2p(v), DOWN, buff=0.22) for v in (0, 20, 40)])
        hops = VGroup(self.hop(line.n2p(0), line.n2p(20), self.BLUE), self.hop(line.n2p(20), line.n2p(40), self.BLUE))
        self.play(FadeIn(marks[0]), Create(hops[0]), FadeIn(marks[1]), run_time=self.rt(n, 0.15))
        self.play(Create(hops[1]), FadeIn(marks[2]), run_time=self.rt(n, 0.15))
        mult = self.tex(r"20 \times 2 = 40", r"\;\Rightarrow\;", r"40 \text{ is a multiple of } 20",
                        size=36, colors={2: self.BLUE}).move_to([1.2, -3.0, 0])
        self.play(FadeIn(mult, shift=UP * 0.1), run_time=self.rt(n, 0.12))
        self.shine(mult[2], self.BLUE, self.rt(n, 0.06))

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
            "Factors divide in; multiples multiply out. Two familiar ideas, ready to build HCF and LCM.",
        )

        # left: arrows point IN to 12;  right: arrows point OUT of 12
        left_c = self.badge(12).move_to([-3.4, -0.6, 0])
        right_c = self.badge(12).move_to([3.4, -0.6, 0])
        ins = VGroup(*[self.badge(v, self.GREEN, radius=0.38, size=30).move_to(p)
                       for v, p in [(2, [-5.3, 0.8, 0]), (3, [-3.4, 1.5, 0]), (4, [-1.5, 0.8, 0])]])
        outs = VGroup(*[self.badge(v, self.BLUE, radius=0.42, size=28).move_to(p)
                        for v, p in [(24, [1.5, 0.8, 0]), (36, [3.4, 1.5, 0]), (48, [5.3, 0.8, 0])]])
        in_arrows = VGroup(*[Arrow(c.get_center(), left_c.get_center(), buff=0.55, color=self.GREEN, stroke_width=4)
                             for c in ins])
        out_arrows = VGroup(*[Arrow(right_c.get_center(), c.get_center(), buff=0.55, color=self.BLUE, stroke_width=4)
                              for c in outs])
        cap_in = self.label("factors divide IN", color=self.GREEN, size=28, weight=BOLD).next_to(left_c, DOWN, buff=0.45)
        cap_out = self.label("multiples multiply OUT", color=self.BLUE, size=28, weight=BOLD).next_to(right_c, DOWN,
                                                                                                    buff=0.45)
        hcf_tag = self.label("→ HCF", color=self.GREEN, size=24).next_to(cap_in, DOWN, buff=0.2)
        lcm_tag = self.label("→ LCM", color=self.BLUE, size=24).next_to(cap_out, DOWN, buff=0.2)

        self.play(FadeIn(left_c), FadeIn(ins), run_time=self.rt(n, 0.1))
        self.play(LaggedStart(*[GrowArrow(a) for a in in_arrows], lag_ratio=0.2), FadeIn(cap_in),
                  run_time=self.rt(n, 0.15))
        self.play(FadeIn(right_c), FadeIn(outs), run_time=self.rt(n, 0.1))
        self.play(LaggedStart(*[GrowArrow(a) for a in out_arrows], lag_ratio=0.2), FadeIn(cap_out),
                  run_time=self.rt(n, 0.15))
        self.play(FadeIn(hcf_tag, lcm_tag, shift=UP * 0.1), run_time=self.rt(n, 0.12))
        self.sweep(VGroup(cap_in, cap_out), self.YELLOW, self.rt(n, 0.1))

        self.wait_for_narration(n)

    # =========================================================
    # 8. DONE / TRANSITION TO COMMON FACTORS
    # =========================================================

    def done(self):

        self.scene_start("done")

        n = self.say("done_01", "That's Factors and Multiples for you — our quick refresher, done.")

        self.clear(self.rt(n, 0.15))
        bf = self.block("factors", self.GREEN).move_to([-1.4, 0.3, 0])
        bm = self.block("multiples", self.BLUE).move_to([1.4, 0.3, 0])
        tick = self.check_mark(self.YELLOW, 2.0).next_to(VGroup(bf, bm), UP, buff=0.5)
        self.play(FadeIn(bf, shift=UP * 0.2), FadeIn(bm, shift=UP * 0.2), run_time=self.rt(n, 0.2))
        self.play(Create(tick), run_time=self.rt(n, 0.15))
        self.shine(tick, self.YELLOW, self.rt(n, 0.1))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Next lesson transition — factors SHARED by two numbers
        # -----------------------------------------------------

        n = self.say("done_02", "In our next video, we look at factors shared between numbers — Common Factors.")

        self.clear(self.rt(n, 0.1))
        nxt = self.label("NEXT VIDEO", color=self.GREY, size=26).move_to(UP * 3.1)
        topic = self.title_text("COMMON FACTORS", color=self.YELLOW, size=56).next_to(nxt, DOWN, buff=0.25)
        a = Circle(radius=1.5, stroke_color=self.GREEN, stroke_width=4, fill_color=self.GREEN,
                   fill_opacity=0.12).move_to([-0.9, -0.9, 0])
        b = Circle(radius=1.5, stroke_color=self.BLUE, stroke_width=4, fill_color=self.BLUE,
                   fill_opacity=0.12).move_to([0.9, -0.9, 0])
        a_lbl = MathTex("12", font_size=40, color=self.GREEN).move_to([-1.7, -0.9, 0])
        b_lbl = MathTex("18", font_size=40, color=self.BLUE).move_to([1.7, -0.9, 0])
        shared = Text("?", font_size=64, color=self.YELLOW, weight=BOLD).move_to([0, -0.9, 0])

        self.play(FadeIn(nxt, shift=DOWN * 0.2), FadeIn(topic, scale=1.1), run_time=self.rt(n, 0.2))
        self.shine(topic, self.YELLOW, self.rt(n, 0.1))
        self.play(Create(a), Create(b), FadeIn(a_lbl, b_lbl), run_time=self.rt(n, 0.2))
        self.play(Write(shared), run_time=self.rt(n, 0.1))
        self.shine(shared, self.YELLOW, self.rt(n, 0.08))

        self.wait_for_narration(n)

        self.see_you_there()

        self.scene_end("done")