from manim import *
from src.animation.lms_scene import LMSScene


class HcfLcmRelationshipVideo(LMSScene):
    """
    HCF x LCM Relationship
    C-CAT | Section A | Module 2: Quantitative Aptitude | Day 3
    HCF & LCM > Relationship Between HCF & LCM

    Visual concept:
        a BALANCE:  HCF x LCM  on one pan,  a x b  on the other  -> always level
        why it always balances: prime BLOCKS
            36 = [2][2][3][3]      60 = [2][2][3][5]
            for each prime, the shorter stack goes to HCF, the taller to LCM,
            so HCF and LCM together use every block exactly once
            -> HCF x LCM is literally the same product as 36 x 60.

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
    YELLOW = "#FFD54A"      # LCM
    PURPLE = "#B388FF"      # HCF
    GREEN = "#69F0AE"       # prime 2 / "it matches"
    BLUE = "#4FC3F7"        # prime 3
    ORANGE = "#FFB74D"      # prime 5
    RED = "#FF5252"
    GREY = "#8A93A6"
    GRID = "#141A26"

    VOICE = "teacher_a"
    PRIME_COLORS = {2: "#69F0AE", 3: "#4FC3F7", 5: "#FFB74D"}

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

    def formula(self, size=52):
        """HCF x LCM = a x b, colour-coded."""
        return self.tex(r"\text{HCF}", r"\times", r"\text{LCM}", "=", "a", r"\times", "b", size=size,
                        colors={0: self.PURPLE, 2: self.YELLOW})

    def balance(self, y=0.6, width=8.0):
        """A level balance. Pans hang from the beam ends; content sits above each pan."""
        beam = Line([-width / 2, y, 0], [width / 2, y, 0], stroke_color=self.WHITE, stroke_width=5)
        fulcrum = Polygon([0, y, 0], [-0.55, y - 1.0, 0], [0.55, y - 1.0, 0], stroke_color=self.GREY,
                          stroke_width=3, fill_color=self.GREY, fill_opacity=0.25)
        pans = VGroup()
        for s in (-1, 1):
            cx = s * width / 2
            pan = Line([cx - 1.7, y - 1.7, 0], [cx + 1.7, y - 1.7, 0], stroke_color=self.WHITE, stroke_width=5)
            strings = VGroup(Line([cx, y, 0], [cx - 1.7, y - 1.7, 0]), Line([cx, y, 0], [cx + 1.7, y - 1.7, 0]))
            strings.set_stroke(self.GREY, 2)
            pans.add(VGroup(strings, pan))
        b = VGroup(fulcrum, beam, pans)
        # content sits low in each pan, where the strings are widest apart
        b.left_spot = np.array([-width / 2, y - 1.4, 0])
        b.right_spot = np.array([width / 2, y - 1.4, 0])
        b.below_left = np.array([-width / 2, y - 2.3, 0])
        b.below_right = np.array([width / 2, y - 2.3, 0])
        return b

    def prime_block(self, p, side=0.5):
        c = self.PRIME_COLORS[p]
        sq = Square(side_length=side, stroke_color=c, stroke_width=2.5, fill_color=c, fill_opacity=0.25)
        return VGroup(sq, MathTex(str(p), font_size=30, color=self.WHITE).move_to(sq))

    def slot_box(self, content, color, width=1.4):
        box = RoundedRectangle(corner_radius=0.12, width=width, height=0.9, stroke_color=color, stroke_width=3,
                               fill_color=color, fill_opacity=0.12)
        return VGroup(box, content.move_to(box))

    # =========================================================
    # 1. HOOK
    # =========================================================

    def hook(self):

        self.scene_start("hook")

        self.open_with_greeting()

        # -----------------------------------------------------
        # Narration 2 — the known results
        # -----------------------------------------------------

        n = self.say("hook_02", "For 36 and 60, we found HCF equals 12, and LCM equals 180.")

        pair = self.tex("36", r",\;", "60", size=64).move_to(UP * 2.6)
        hcf = self.tex(r"\text{HCF}", "=", "12", size=48, colors={0: self.PURPLE, 2: self.PURPLE}).move_to([-3.0, 1.2, 0])
        lcm = self.tex(r"\text{LCM}", "=", "180", size=48, colors={0: self.YELLOW, 2: self.YELLOW}).move_to([3.0, 1.2, 0])
        self.play(Write(pair), run_time=self.rt(n, 0.2))
        self.play(FadeIn(hcf, shift=DOWN * 0.2), run_time=self.rt(n, 0.2))
        self.play(FadeIn(lcm, shift=DOWN * 0.2), run_time=self.rt(n, 0.2))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — multiply HCF and LCM
        # -----------------------------------------------------

        n = self.say("hook_03", "Now multiply them — 12 times 180.")

        self.left_q = self.tex("12", r"\times", "180", "=", "?", size=52,
                               colors={0: self.PURPLE, 2: self.YELLOW, 4: self.GREY}).move_to([-3.2, -0.6, 0])
        self.play(TransformFromCopy(hcf[2], self.left_q[0]), TransformFromCopy(lcm[2], self.left_q[2]),
                  FadeIn(self.left_q[1]), run_time=self.rt(n, 0.35))
        self.play(FadeIn(self.left_q[3:]), run_time=self.rt(n, 0.15))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 4 — compare with the numbers themselves
        # -----------------------------------------------------

        n = self.say("hook_04", "What do you notice, compared to multiplying 36 and 60 themselves?")

        self.right_q = self.tex("36", r"\times", "60", "=", "?", size=52, colors={4: self.GREY}).move_to([3.2, -0.6, 0])
        self.play(TransformFromCopy(pair[0], self.right_q[0]), TransformFromCopy(pair[2], self.right_q[2]),
                  FadeIn(self.right_q[1], self.right_q[3:]), run_time=self.rt(n, 0.3))
        vs = MathTex(r"\overset{?}{=}", font_size=64, color=self.YELLOW).move_to([0, -0.6, 0])
        self.play(Write(vs), run_time=self.rt(n, 0.15))
        self.shine(vs, self.YELLOW, self.rt(n, 0.1))

        self.wait_for_narration(n)

    # =========================================================
    # 2. INTRODUCTION
    # =========================================================

    def introduction(self):

        self.scene_start("introduction")

        n = self.say("intro_01", "Welcome back! Today we uncover a genuinely beautiful fact — the HCF × LCM Relationship.")

        self.clear(self.rt(n, 0.12))
        title = self.title_text("HCF × LCM RELATIONSHIP", color=self.YELLOW, size=58).move_to(UP * 0.5)
        sub = self.label("a genuinely beautiful fact", color=self.GREY, size=28).next_to(title, DOWN, buff=0.4)
        self.play(FadeIn(title, scale=1.1), run_time=self.rt(n, 0.2))
        self.shine(title, self.YELLOW, self.rt(n, 0.12))
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=self.rt(n, 0.15))
        self.sweep(title, self.YELLOW, self.rt(n, 0.15))

        self.wait_for_narration(n)

    # =========================================================
    # 3. HOW — the rule, as a balance
    # =========================================================

    def how(self):

        self.scene_start("how")

        n = self.say("how_01", "So what exactly is this relationship?")

        self.clear(self.rt(n, 0.25))
        self.bal = self.balance()
        self.play(FadeIn(self.bal, shift=UP * 0.2), run_time=self.rt(n, 0.35))

        self.wait_for_narration(n)

        n = self.say(
            "how_02",
            "My dear students, for any two numbers, their HCF multiplied by their LCM always equals "
            "the product of the two numbers themselves.",
        )

        self.rule = self.formula().move_to(UP * 2.9)
        left_side = self.tex(r"\text{HCF}", r"\times", r"\text{LCM}", size=40,
                             colors={0: self.PURPLE, 2: self.YELLOW}).move_to(self.bal.left_spot)
        right_side = self.tex("a", r"\times", "b", size=44).move_to(self.bal.right_spot)

        self.play(Write(self.rule[0:3]), run_time=self.rt(n, 0.18))
        self.play(TransformFromCopy(self.rule[0:3], left_side), run_time=self.rt(n, 0.15))
        self.play(Write(self.rule[3:]), run_time=self.rt(n, 0.15))
        self.play(TransformFromCopy(self.rule[4:], right_side), run_time=self.rt(n, 0.15))
        # the beam stays perfectly level
        self.play(Wiggle(self.bal[1], scale_value=1.02, rotation_angle=0.015 * TAU), run_time=self.rt(n, 0.12))
        self.shine(self.rule, self.YELLOW, self.rt(n, 0.08))
        self.pan_content = VGroup(left_side, right_side)

        self.wait_for_narration(n)

    # =========================================================
    # 4. WHAT — check it, then see why it always works
    # =========================================================

    def what(self):

        self.scene_start("what")

        # -----------------------------------------------------
        # Narration 1 — left pan
        # -----------------------------------------------------

        n = self.say("what_01", "12 times 180 equals 2,160.")

        left_val = self.tex("12", r"\times", "180", size=42, colors={0: self.PURPLE, 2: self.YELLOW})
        left_val.move_to(self.bal.left_spot)
        left_res = MathTex("2160", font_size=52, color=self.GREEN).move_to(self.bal.below_left)
        self.play(Transform(self.pan_content[0], left_val), run_time=self.rt(n, 0.3))
        self.play(FadeIn(left_res, shift=DOWN * 0.2), run_time=self.rt(n, 0.25))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — right pan
        # -----------------------------------------------------

        n = self.say("what_02", "And 36 times 60 also equals 2,160.")

        right_val = self.tex("36", r"\times", "60", size=42).move_to(self.bal.right_spot)
        right_res = MathTex("2160", font_size=52, color=self.GREEN).move_to(self.bal.below_right)
        self.play(Transform(self.pan_content[1], right_val), run_time=self.rt(n, 0.25))
        self.play(FadeIn(right_res, shift=DOWN * 0.2), run_time=self.rt(n, 0.2))
        level = VGroup(self.check_mark(self.GREEN, 1.4),
                       self.label("perfectly level", color=self.GREEN, size=26, weight=BOLD)).arrange(RIGHT, buff=0.2)
        level.move_to([0, -1.6, 0])
        self.play(FadeIn(level, shift=UP * 0.1), run_time=self.rt(n, 0.15))
        self.sweep(VGroup(left_res, right_res), self.GREEN, self.rt(n, 0.12))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — why it never fails: the same blocks, re-sorted
        # -----------------------------------------------------

        n = self.say(
            "what_03",
            "They match, perfectly, every single time — not just for this pair, but for any two numbers at all.",
        )

        self.play(FadeOut(self.bal, self.pan_content, left_res, right_res, level),
                  self.rule.animate.scale(0.7).to_edge(UP, buff=0.3), run_time=self.rt(n, 0.1))

        def row(name, primes, y, color=None):
            lbl = MathTex(name, "=", font_size=40, color=color or self.WHITE).move_to([-5.0, y, 0])
            blocks = VGroup(*[self.prime_block(p) for p in primes]).arrange(RIGHT, buff=0.1)
            blocks.next_to(lbl, RIGHT, buff=0.3)
            return lbl, blocks

        l36, b36 = row("36", [2, 2, 3, 3], 1.9)
        l60, b60 = row("60", [2, 2, 3, 5], 1.0)
        lh, _ = row(r"\text{HCF}", [2, 2, 3], -0.7, self.PURPLE)
        ll, _ = row(r"\text{LCM}", [2, 2, 3, 3, 5], -1.7, self.YELLOW)
        lh.align_to(ll, RIGHT)
        slots_h = [lh.get_right() + RIGHT * (0.55 + 0.6 * i) for i in range(3)]
        slots_l = [ll.get_right() + RIGHT * (0.55 + 0.6 * i) for i in range(5)]

        self.play(FadeIn(l36, b36, l60, b60, shift=RIGHT * 0.2), run_time=self.rt(n, 0.12))
        self.play(FadeIn(lh, ll), run_time=self.rt(n, 0.06))

        # for each prime: the shorter stack -> HCF, the taller -> LCM
        to_hcf = [(b36[0], 0), (b36[1], 1), (b60[2], 2)]
        to_lcm = [(b60[0], 0), (b60[1], 1), (b36[2], 2), (b36[3], 3), (b60[3], 4)]
        self.play(*[blk.animate.move_to([slots_h[i][0], lh.get_y(), 0]) for blk, i in to_hcf],
                  run_time=self.rt(n, 0.16))
        self.play(*[blk.animate.move_to([slots_l[i][0], ll.get_y(), 0]) for blk, i in to_lcm],
                  run_time=self.rt(n, 0.16))
        eq_h = MathTex("= 12", font_size=40, color=self.PURPLE).next_to(
            VGroup(*[blk for blk, _ in to_hcf]), RIGHT, buff=0.3)
        eq_l = MathTex("= 180", font_size=40, color=self.YELLOW).next_to(
            VGroup(*[blk for blk, _ in to_lcm]), RIGHT, buff=0.3)
        self.play(FadeIn(eq_h, eq_l), FadeOut(l36, l60), run_time=self.rt(n, 0.08))
        caption = self.label("the same blocks, just re-sorted → the same product, for any two numbers",
                             color=self.GREEN, size=26).move_to(DOWN * 3.0)
        self.play(FadeIn(caption, shift=UP * 0.1), run_time=self.rt(n, 0.1))
        self.shine(caption, self.GREEN, self.rt(n, 0.06))

        self.wait_for_narration(n)

    # =========================================================
    # 5. WHY — know any three, find the fourth
    # =========================================================

    def why(self):

        self.scene_start("why")

        n = self.say("why_01", "Now, why does this matter?")

        self.clear(self.rt(n, 0.25))
        values = ["36", "60", "12", "180"]
        colors = [self.WHITE, self.WHITE, self.PURPLE, self.YELLOW]
        self.slots = [self.slot_box(MathTex(v, font_size=44, color=c), c) for v, c in zip(values, colors)]
        times1 = MathTex(r"\times", font_size=48)
        eq = MathTex("=", font_size=52)
        times2 = MathTex(r"\times", font_size=48)
        row = VGroup(self.slots[0], times1, self.slots[1], eq, self.slots[2], times2, self.slots[3])
        row.arrange(RIGHT, buff=0.3).move_to(UP * 0.8)
        names = VGroup(*[self.label(t, color=c, size=22).next_to(s, UP, buff=0.2)
                         for t, c, s in zip(["a", "b", "HCF", "LCM"], colors, self.slots)])
        self.play(FadeIn(row, shift=UP * 0.2), FadeIn(names), run_time=self.rt(n, 0.35))

        self.wait_for_narration(n)

        n = self.say(
            "why_02",
            "Because this relationship lets you find any one of these four values — the two numbers, the HCF, "
            "or the LCM — if you already know the other three, without repeating a full calculation.",
        )

        # each slot in turn goes missing; the other three bring it back
        for i, slot in enumerate(self.slots):
            original = slot[1].copy()
            q = Text("?", font_size=48, color=self.RED, weight=BOLD).move_to(slot[1])
            self.play(Transform(slot[1], q), run_time=self.rt(n, 0.06))
            others = VGroup(*[s for j, s in enumerate(self.slots) if j != i])
            self.play(Indicate(others, color=self.GREEN, scale_factor=1.04), run_time=self.rt(n, 0.08))
            self.play(Transform(slot[1], original), Flash(slot, color=self.GREEN, flash_radius=0.8),
                      run_time=self.rt(n, 0.06))
        cap = self.label("know any 3  →  find the 4th", color=self.GREEN, size=32, weight=BOLD).move_to(DOWN * 1.5)
        self.play(FadeIn(cap, shift=UP * 0.2), run_time=self.rt(n, 0.1))
        self.shine(cap, self.GREEN, self.rt(n, 0.06))

        self.wait_for_narration(n)

    # =========================================================
    # 6. REAL WORLD EXAMPLE
    # =========================================================

    def real_world_example(self):

        self.scene_start("real_world")

        n = self.say(
            "example_01",
            "Let me tell you about a girl named Anandita, given that two numbers have an HCF of 5 "
            "and an LCM of 60, and asked for their product.",
        )

        anandita = self.person(self.ORANGE).scale(0.6).move_to([-5.9, 0.3, 0])
        name = self.label("Anandita", color=self.YELLOW, size=24).next_to(anandita, DOWN, buff=0.2)
        self.slide_board(VGroup(anandita, name), LEFT, self.rt(n, 0.15))

        hcf = self.slot_box(MathTex("5", font_size=48, color=self.PURPLE), self.PURPLE).move_to([-1.8, 2.3, 0])
        lcm = self.slot_box(MathTex("60", font_size=48, color=self.YELLOW), self.YELLOW).move_to([1.8, 2.3, 0])
        hcf_n = self.label("HCF", color=self.PURPLE, size=24).next_to(hcf, UP, buff=0.15)
        lcm_n = self.label("LCM", color=self.YELLOW, size=24).next_to(lcm, UP, buff=0.15)
        self.play(FadeIn(hcf, hcf_n, shift=DOWN * 0.2), run_time=self.rt(n, 0.12))
        self.play(FadeIn(lcm, lcm_n, shift=DOWN * 0.2), run_time=self.rt(n, 0.12))

        # the two numbers themselves stay hidden
        mystery = VGroup(self.slot_box(Text("?", font_size=44, color=self.GREY, weight=BOLD), self.GREY),
                         MathTex(r"\times", font_size=48),
                         self.slot_box(Text("?", font_size=44, color=self.GREY, weight=BOLD), self.GREY),
                         MathTex("=", font_size=52),
                         self.slot_box(Text("?", font_size=44, color=self.GREEN, weight=BOLD), self.GREEN, width=1.8))
        mystery.arrange(RIGHT, buff=0.3).move_to([0, 0.2, 0])
        self.play(FadeIn(mystery, shift=UP * 0.2), run_time=self.rt(n, 0.15))

        self.wait_for_narration(n)

        n = self.say(
            "example_02",
            "She simply multiplied 5 by 60, instantly finding the product of the two numbers to be 300, "
            "without ever needing to know the numbers themselves.",
        )

        calc = self.tex("5", r"\times", "60", "=", "300", size=56,
                        colors={0: self.PURPLE, 2: self.YELLOW, 4: self.GREEN}).move_to([0, -1.6, 0])
        self.play(TransformFromCopy(hcf[1], calc[0]), TransformFromCopy(lcm[1], calc[2]), FadeIn(calc[1]),
                  run_time=self.rt(n, 0.18))
        self.play(Write(calc[3:]), run_time=self.rt(n, 0.12))
        self.shine(calc[4], self.GREEN, self.rt(n, 0.06))
        answer = MathTex("300", font_size=44, color=self.GREEN).move_to(mystery[4][1])
        self.play(Transform(mystery[4][1], answer), Flash(mystery[4], color=self.GREEN, flash_radius=1.0),
                  run_time=self.rt(n, 0.15))
        never = self.label("the two numbers are never needed", color=self.GREY, size=24).move_to(DOWN * 2.9)
        self.play(FadeIn(never), Indicate(VGroup(mystery[0], mystery[2]), color=self.GREY), run_time=self.rt(n, 0.12))

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
            "For any two numbers, HCF times LCM always equals their product — "
            "a genuinely elegant shortcut, worth remembering.",
        )

        rule = self.formula(size=64).move_to(UP * 1.2)
        frame = SurroundingRectangle(rule, color=self.YELLOW, buff=0.35, corner_radius=0.15)
        bal = self.balance(y=-0.6, width=6.0)
        bal.scale(0.7).move_to(DOWN * 1.9)
        self.play(Write(rule), run_time=self.rt(n, 0.3))
        self.play(Create(frame), run_time=self.rt(n, 0.12))
        self.shine(frame, self.YELLOW, self.rt(n, 0.1))
        self.play(FadeIn(bal, shift=UP * 0.2), run_time=self.rt(n, 0.15))

        self.wait_for_narration(n)

    # =========================================================
    # 8. DONE
    # =========================================================

    def done(self):

        self.scene_start("done")

        n = self.say("done_01", "That's the HCF times LCM Relationship for you — a beautiful, reliable link.")

        self.clear(self.rt(n, 0.12))
        left = self.tex(r"\text{HCF}", r"\times", r"\text{LCM}", size=56, colors={0: self.PURPLE, 2: self.YELLOW})
        right = self.tex("a", r"\times", "b", size=56)
        left.move_to([-3.2, 0.3, 0])
        right.move_to([3.2, 0.3, 0])
        chain = VGroup(*[Ellipse(width=0.9, height=0.5, stroke_color=self.GREEN, stroke_width=5) for _ in range(3)])
        chain.arrange(RIGHT, buff=-0.25).move_to([0, 0.3, 0])
        self.play(FadeIn(left, shift=RIGHT * 0.2), FadeIn(right, shift=LEFT * 0.2), run_time=self.rt(n, 0.2))
        self.play(LaggedStart(*[Create(c) for c in chain], lag_ratio=0.3), run_time=self.rt(n, 0.2))
        self.shine(chain, self.GREEN, self.rt(n, 0.12))

        self.wait_for_narration(n)

        n = self.say(
            "done_02",
            "In our next video, we see what changes with three or more numbers — Applications to Two or More Numbers.",
        )

        self.clear(self.rt(n, 0.1))
        nxt = self.label("NEXT VIDEO", color=self.GREY, size=26).move_to(UP * 2.7)
        topic = self.title_text("APPLICATIONS TO TWO OR MORE NUMBERS", color=self.YELLOW, size=42)
        topic.next_to(nxt, DOWN, buff=0.3)
        trio = VGroup(*[self.slot_box(MathTex(v, font_size=44), c) for v, c in
                        [("a", self.GREEN), ("b", self.BLUE), ("c", self.ORANGE)]]).arrange(RIGHT, buff=0.6)
        trio.move_to(DOWN * 0.6)
        q = Text("?", font_size=64, color=self.YELLOW, weight=BOLD).next_to(trio, RIGHT, buff=0.6)
        self.play(FadeIn(nxt, shift=DOWN * 0.2), FadeIn(topic, scale=1.05), run_time=self.rt(n, 0.2))
        self.shine(topic, self.YELLOW, self.rt(n, 0.1))
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in trio], lag_ratio=0.25), run_time=self.rt(n, 0.2))
        self.play(Write(q), run_time=self.rt(n, 0.1))

        self.wait_for_narration(n)

        self.see_you_there()

        self.scene_end("done")