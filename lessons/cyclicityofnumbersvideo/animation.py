from manim import *
from src.animation.lms_scene import LMSScene


class CyclicityOfNumbersVideo(LMSScene):
    """
    Cyclicity of Numbers
    C-CAT | Section A | Module 2: Quantitative Aptitude | Day 3
    Number Systems > Last Digit & Unit Digit

    Visual concept: every digit gets a CYCLE WHEEL — the unit digits of its
    powers placed around a circle, with a dot that keeps travelling round.
        length 1 (stay still):  0, 1, 5, 6
        length 2 (flip in pairs): 4 -> 6,   9 -> 1
        length 4 (dance in fours): 2 -> 4 -> 8 -> 6,   3 -> 9 -> 7 -> 1,
                                   7 -> 9 -> 3 -> 1,   8 -> 4 -> 2 -> 6
    The three families are always shown in the same three colours.

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
    YELLOW = "#FFD54A"      # answers
    GREEN = "#69F0AE"       # cycle length 1
    BLUE = "#4FC3F7"        # cycle length 2
    ORANGE = "#FFB74D"      # cycle length 4
    RED = "#FF5252"
    PURPLE = "#B388FF"
    GREY = "#8A93A6"
    GRID = "#141A26"

    VOICE = "teacher_a"

    CYCLES = {
        0: [0], 1: [1], 5: [5], 6: [6],
        4: [4, 6], 9: [9, 1],
        2: [2, 4, 8, 6], 3: [3, 9, 7, 1], 7: [7, 9, 3, 1], 8: [8, 4, 2, 6],
    }
    FAMILIES = [
        ([0, 1, 5, 6], 1, "stay still"),
        ([4, 9], 2, "flip in pairs"),
        ([2, 3, 7, 8], 4, "dance in fours"),
    ]

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

    def family_color(self, digit):
        n = len(self.CYCLES[digit])
        return {1: self.GREEN, 2: self.BLUE, 4: self.ORANGE}[n]

    def digit_tile(self, d, color=None, side=0.8):
        c = color or self.GREY
        sq = RoundedRectangle(corner_radius=0.1, width=side, height=side, stroke_color=c, stroke_width=3,
                              fill_color=c, fill_opacity=0.12)
        return VGroup(sq, MathTex(str(d), font_size=int(side * 55), color=c).move_to(sq))

    def wheel(self, d, radius=0.62):
        """Cycle wheel: base digit in the centre, unit digits of its powers around the rim."""
        color = self.family_color(d)
        cyc = self.CYCLES[d]
        ring = Circle(radius=radius, stroke_color=color, stroke_width=3)
        centre = MathTex(rf"{d}^n", font_size=30, color=self.GREY)
        rim = VGroup()
        for k, u in enumerate(cyc):
            angle = PI / 2 - k * TAU / len(cyc)
            pos = radius * np.array([np.cos(angle), np.sin(angle), 0])
            disc = Circle(radius=0.2, stroke_color=color, stroke_width=2, fill_color=self.BG, fill_opacity=1).move_to(pos)
            rim.add(VGroup(disc, MathTex(str(u), font_size=28, color=color).move_to(pos)))
        traveller = Dot(rim[0].get_center(), radius=0.07, color=self.YELLOW)
        w = VGroup(ring, centre, rim, traveller)
        w.ring, w.rim, w.traveller, w.digit = ring, rim, traveller, d
        return w

    def spin(self, w, turns=1):
        """The traveller goes round the wheel: the unit digit repeating."""
        return Rotate(w.traveller, angle=-TAU * turns, about_point=w.ring.get_center())

    def map_card(self, size=30, show_lengths=True):
        """The complete map: family colour, length, digits, nickname."""
        rows = VGroup()
        for digits, length, nick in self.FAMILIES:
            c = self.family_color(digits[0])
            parts = [MathTex(r",\ ".join(str(d) for d in digits), font_size=size + 8, color=c)]
            if show_lengths:
                parts.insert(0, self.label(f"length {length}", color=c, size=size - 4, weight=BOLD))
            parts.append(self.label(nick, color=self.GREY, size=size - 6))
            rows.add(VGroup(*parts).arrange(RIGHT, buff=0.4))
        rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        return rows

    # =========================================================
    # 1. HOOK
    # =========================================================

    def hook(self):

        self.scene_start("hook")

        self.open_with_greeting()

        # -----------------------------------------------------
        # Narration 2 — which digit never changes?
        # -----------------------------------------------------

        n = self.say(
            "hook_02",
            "Which digit do you think has the shortest possible cycle — a cycle of just length one, "
            "where the unit digit never even changes?",
        )

        self.tiles = VGroup(*[self.digit_tile(d) for d in range(10)]).arrange(RIGHT, buff=0.22).move_to(UP * 0.6)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in self.tiles], lag_ratio=0.08),
                  run_time=self.rt(n, 0.25))
        ask = self.tex(r"\text{cycle length}", "=", "1", r"\;?", size=48, colors={2: self.GREEN, 3: self.YELLOW})
        ask.move_to(DOWN * 1.2)
        self.play(Write(ask), run_time=self.rt(n, 0.2))
        self.play(LaggedStart(*[Indicate(t, color=self.YELLOW, scale_factor=1.1) for t in self.tiles], lag_ratio=0.08),
                  run_time=self.rt(n, 0.25))
        self.ask = ask

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — four of them
        # -----------------------------------------------------

        n = self.say("hook_03", "There are actually four of them! Let's meet every digit's cycle length today.")

        four = VGroup(*[self.digit_tile("?", self.GREEN, side=0.9) for _ in range(4)]).arrange(RIGHT, buff=0.25)
        four.move_to(DOWN * 2.6)
        self.play(LaggedStart(*[FadeIn(f, scale=0.6) for f in four], lag_ratio=0.2), run_time=self.rt(n, 0.25))
        self.shine(four, self.GREEN, self.rt(n, 0.1))

        self.wait_for_narration(n)

    # =========================================================
    # 2. INTRODUCTION
    # =========================================================

    def introduction(self):

        self.scene_start("introduction")

        n = self.say(
            "intro_01",
            "Welcome back! Today we step back and study Cyclicity of Numbers — "
            "the complete pattern behind every digit, 0 through 9.",
        )

        self.clear(self.rt(n, 0.12), keep=[self.tiles])
        title = self.title_text("CYCLICITY OF NUMBERS", color=self.YELLOW, size=58).move_to(UP * 2.4)
        self.play(FadeIn(title, scale=1.1), self.tiles.animate.move_to(DOWN * 0.3), run_time=self.rt(n, 0.2))
        self.shine(title, self.YELLOW, self.rt(n, 0.1))
        span = Brace(self.tiles, DOWN, buff=0.2, color=self.GREY)
        span_lbl = self.label("every digit, 0 through 9", color=self.GREY, size=26).next_to(span, DOWN, buff=0.15)
        self.play(GrowFromCenter(span), FadeIn(span_lbl), run_time=self.rt(n, 0.15))
        # each tile takes on its family colour — the map we are about to build
        self.play(LaggedStart(*[
            t.animate.set_color(self.family_color(d)) for d, t in enumerate(self.tiles)
        ], lag_ratio=0.1), run_time=self.rt(n, 0.25))

        self.wait_for_narration(n)

    # =========================================================
    # 3. HOW — list powers, watch for the repeat
    # =========================================================

    def how(self):

        self.scene_start("how")

        n = self.say("how_01", "So how do we map this out?")

        self.clear(self.rt(n, 0.3))
        head = self.label("POWERS OF 2", color=self.ORANGE, size=28, weight=BOLD).to_corner(UL, buff=0.5)
        self.play(FadeIn(head), run_time=self.rt(n, 0.2))

        self.wait_for_narration(n)

        n = self.say(
            "how_02",
            "My dear students, list the powers of each digit, one by one, "
            "and watch exactly when the unit digit starts repeating itself.",
        )

        xs = [-5.6 + 1.2 * k for k in range(8)]
        powers = VGroup(*[MathTex(rf"2^{k + 1}", font_size=40).move_to([x, 1.7, 0]) for k, x in enumerate(xs)])
        values = VGroup(*[MathTex(str(2 ** (k + 1)), font_size=36, color=self.GREY).move_to([x, 0.8, 0])
                          for k, x in enumerate(xs)])
        units = VGroup(*[self.digit_tile(2 ** (k + 1) % 10, self.ORANGE, side=0.7).move_to([x, -0.3, 0])
                         for k, x in enumerate(xs)])

        for k in range(8):
            self.play(FadeIn(powers[k], shift=DOWN * 0.1), FadeIn(values[k]), run_time=self.rt(n, 0.04))
            self.play(TransformFromCopy(values[k][0][-1], units[k]), run_time=self.rt(n, 0.04))
        # the moment it repeats: 2^5 ends in 2 again
        cycle_brace = Brace(units[0:4], DOWN, buff=0.15, color=self.ORANGE)
        cycle_lbl = self.label("one cycle", color=self.ORANGE, size=24).next_to(cycle_brace, DOWN, buff=0.1)
        again = CurvedArrow(units[4].get_bottom() + DOWN * 0.1, units[0].get_bottom() + DOWN * 0.1,
                            angle=-PI / 3, color=self.YELLOW, stroke_width=3)
        self.play(GrowFromCenter(cycle_brace), FadeIn(cycle_lbl), run_time=self.rt(n, 0.1))
        self.play(Indicate(units[4], color=self.YELLOW, scale_factor=1.2), Create(again), run_time=self.rt(n, 0.12))

        # fold the first cycle into a wheel
        w2 = self.wheel(2, radius=0.9).move_to([5.2, -0.3, 0])
        self.play(Create(w2.ring), FadeIn(w2[1]), run_time=self.rt(n, 0.06))
        self.play(*[TransformFromCopy(units[k], w2.rim[k]) for k in range(4)], run_time=self.rt(n, 0.1))
        self.play(FadeIn(w2.traveller), self.spin(w2), run_time=self.rt(n, 0.08))

        self.wait_for_narration(n)

    # =========================================================
    # 4. WHAT — the three families
    # =========================================================

    def what(self):

        self.scene_start("what")

        rows_y = [2.2, 0.35, -1.55]
        xs = [-2.9, -1.1, 0.7, 2.5]
        self.wheels = {}
        texts = [
            "Digits 0, 1, 5, and 6 have a cycle length of just 1 — "
            "their unit digit simply never changes, no matter the power.",
            "Digits 4 and 9 have a cycle length of 2.",
            "And digits 2, 3, 7, and 8 each have the longest cycle length, 4.",
        ]
        self.row_labels = VGroup()

        for k, ((digits, length, nick), y, text) in enumerate(zip(self.FAMILIES, rows_y, texts)):
            n = self.say(f"what_0{k + 1}", text)
            if k == 0:
                self.clear(self.rt(n, 0.08))
            c = self.family_color(digits[0])
            lbl = VGroup(self.label(f"length {length}", color=c, size=26, weight=BOLD),
                         self.label(nick, color=self.GREY, size=20)).arrange(DOWN, buff=0.08)
            lbl.move_to([-5.4, y, 0])
            ws = [self.wheel(d).move_to([x, y, 0]) for d, x in zip(digits, xs)]
            for d, w in zip(digits, ws):
                self.wheels[d] = w
            self.row_labels.add(lbl)

            self.play(FadeIn(lbl, shift=RIGHT * 0.2), run_time=self.rt(n, 0.1))
            self.play(LaggedStart(*[AnimationGroup(Create(w.ring), FadeIn(w[1]), FadeIn(w.rim))
                                    for w in ws], lag_ratio=0.2), run_time=self.rt(n, 0.3))
            self.play(*[FadeIn(w.traveller) for w in ws], run_time=self.rt(n, 0.06))
            self.play(*[self.spin(w, turns=2) for w in ws], run_time=self.rt(n, 0.3), rate_func=linear)
            self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 4 — memorise the lengths, skip the powers
        # -----------------------------------------------------

        n = self.say(
            "what_04",
            "Knowing these lengths by heart means you never need to write out a single power "
            "before solving a unit digit question.",
        )

        card = self.map_card(size=24, show_lengths=False)
        frame = RoundedRectangle(corner_radius=0.2, width=card.width + 0.6, height=card.height + 0.9,
                                 stroke_color=self.YELLOW, stroke_width=3, fill_color=self.BG, fill_opacity=0.9)
        card_title = self.label("BY HEART", color=self.YELLOW, size=22, weight=BOLD)
        box = VGroup(frame, card_title, card)
        card.move_to(frame.get_center() + DOWN * 0.2)
        card_title.move_to(frame.get_top() + DOWN * 0.3)
        box.move_to([5.2, 0.3, 0])
        if box.width > 3.6:
            box.scale_to_fit_width(3.6)
        self.play(FadeIn(box, shift=LEFT * 0.3), run_time=self.rt(n, 0.25))
        self.shine(frame, self.YELLOW, self.rt(n, 0.12))
        self.play(*[self.spin(w) for w in self.wheels.values()], run_time=self.rt(n, 0.3), rate_func=linear)
        self.map_box = box

        self.wait_for_narration(n)

    # =========================================================
    # 5. WHY — instant lookup vs. working it out
    # =========================================================

    def why(self):

        self.scene_start("why")

        n = self.say("why_01", "Now, why does this matter?")

        self.clear(self.rt(n, 0.25))
        question = self.tex(r"\text{unit digit of }", "7^{50}", r"\;?", size=52, colors={1: self.ORANGE, 2: self.YELLOW})
        question.move_to(UP * 2.8)
        self.play(Write(question), run_time=self.rt(n, 0.35))

        self.wait_for_narration(n)

        n = self.say(
            "why_02",
            "Because memorising these cycle lengths in advance turns every unit digit question into an "
            "instant lookup, rather than something you need to work out fresh each time.",
        )

        # the slow way: writing out powers one after another
        slow = VGroup(*[MathTex(rf"7^{k} = {7 ** k}", font_size=30, color=self.GREY) for k in range(1, 7)])
        slow.add(MathTex(r"\vdots", font_size=30, color=self.GREY))
        slow.arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to([-3.8, -0.4, 0])
        slow_lbl = self.label("working it out fresh", color=self.GREY, size=24).next_to(slow, UP, buff=0.3)
        self.play(FadeIn(slow_lbl), LaggedStart(*[FadeIn(s) for s in slow], lag_ratio=0.15), run_time=self.rt(n, 0.25))
        cross = VGroup(Line(slow.get_corner(UL), slow.get_corner(DR)), Line(slow.get_corner(UR), slow.get_corner(DL)))
        cross.set_stroke(self.RED, 6)
        self.play(Create(cross), run_time=self.rt(n, 0.08))

        # the fast way: look it up on the map
        card = self.map_card(size=26)
        card.move_to([3.4, -0.2, 0])
        if card.width > 6.4:
            card.scale_to_fit_width(6.4)
        lookup_lbl = self.label("instant lookup", color=self.YELLOW, size=24, weight=BOLD).next_to(card, UP, buff=0.4)
        self.play(FadeIn(card, shift=LEFT * 0.2), FadeIn(lookup_lbl), run_time=self.rt(n, 0.15))
        self.play(Circumscribe(card[2], color=self.ORANGE, time_width=0.8), run_time=self.rt(n, 0.12))
        self.shine(lookup_lbl, self.YELLOW, self.rt(n, 0.08))

        self.wait_for_narration(n)

    # =========================================================
    # 6. REAL WORLD EXAMPLE
    # =========================================================

    def real_world_example(self):

        self.scene_start("real_world")

        n = self.say(
            "example_01",
            'Let me tell you about a boy named Rajveer, who kept a small mental note — '
            '"0, 1, 5, 6 stay still; 4 and 9 flip in pairs; 2, 3, 7, 8 dance in fours."',
        )

        rajveer = self.person(self.PURPLE).scale(0.6).move_to([-5.8, -1.2, 0])
        name = self.label("Rajveer", color=self.YELLOW, size=24).next_to(rajveer, DOWN, buff=0.2)
        self.slide_board(VGroup(rajveer, name), LEFT, self.rt(n, 0.12))

        # a thought bubble holding the note
        note = self.map_card(size=26, show_lengths=False)
        cloud = Ellipse(width=note.width + 1.4, height=note.height + 1.2, stroke_color=self.WHITE, stroke_width=2.5,
                        fill_color=self.BG, fill_opacity=1)
        bubble = VGroup(cloud, note.move_to(cloud)).move_to([0.8, 1.4, 0])
        puffs = VGroup(*[Circle(radius=r, stroke_color=self.WHITE, stroke_width=2.5).move_to(p)
                         for r, p in [(0.12, [-5.1, -0.1, 0]), (0.18, [-4.6, 0.3, 0]), (0.24, [-3.9, 0.7, 0])]])
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in puffs], lag_ratio=0.3), run_time=self.rt(n, 0.1))
        self.play(FadeIn(cloud, scale=0.9), run_time=self.rt(n, 0.08))
        for row in note:
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=self.rt(n, 0.15))
        self.bubble = VGroup(puffs, bubble)

        self.wait_for_narration(n)

        n = self.say(
            "example_02",
            "When asked for the unit digit of 6 raised to the power 82, he instantly knew — "
            "since 6 never changes, the answer was simply 6, without a single calculation.",
        )

        q = self.tex(r"\text{unit digit of }", "6^{82}", "=", "?", size=48,
                     colors={1: self.GREEN, 3: self.YELLOW}).move_to([1.6, -1.7, 0])
        self.play(Write(q), run_time=self.rt(n, 0.15))
        self.play(Circumscribe(note[0], color=self.GREEN), run_time=self.rt(n, 0.12))

        w6 = self.wheel(6, radius=0.6).next_to(q, RIGHT, buff=0.6)
        self.play(FadeIn(w6), run_time=self.rt(n, 0.08))
        # lap after lap, the dot only ever lands on 6
        self.play(self.spin(w6, turns=3), run_time=self.rt(n, 0.15), rate_func=linear)
        self.play(Indicate(w6.rim[0], color=self.YELLOW, scale_factor=1.3), run_time=self.rt(n, 0.06))
        ans = MathTex("6", font_size=56, color=self.YELLOW).move_to(q[3])
        self.play(Transform(q[3], ans), Flash(ans, color=self.YELLOW, flash_radius=0.5), run_time=self.rt(n, 0.12))
        instant = self.label("no calculation", color=self.GREEN, size=26, weight=BOLD).next_to(q, DOWN, buff=0.4)
        self.play(FadeIn(instant, shift=UP * 0.1), run_time=self.rt(n, 0.08))
        self.shine(ans, self.YELLOW, self.rt(n, 0.06))

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
            "Cycle length 1 belongs to 0, 1, 5, and 6. Cycle length 2 belongs to 4 and 9. "
            "Cycle length 4 belongs to 2, 3, 7, and 8. Learn this map, and unit digit questions become instant.",
        )

        card = self.map_card(size=34).move_to(DOWN * 0.4)
        for row in card:
            self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=self.rt(n, 0.18))
        frame = SurroundingRectangle(card, color=self.YELLOW, buff=0.4, corner_radius=0.2)
        self.play(Create(frame), run_time=self.rt(n, 0.12))
        self.shine(frame, self.YELLOW, self.rt(n, 0.1))

        self.wait_for_narration(n)

    # =========================================================
    # 8. DONE
    # =========================================================

    def done(self):

        self.scene_start("done")

        n = self.say("done_01", "That's Cyclicity of Numbers for you — the complete map, now in your hands.")

        self.clear(self.rt(n, 0.12))
        tiles = VGroup(*[self.digit_tile(d, self.family_color(d)) for d in range(10)]).arrange(RIGHT, buff=0.22)
        tiles.move_to(UP * 0.3)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in tiles], lag_ratio=0.08), run_time=self.rt(n, 0.3))
        self.sweep(tiles, self.YELLOW, self.rt(n, 0.15))

        self.wait_for_narration(n)

        n = self.say("done_02", "In our next video, we go one step further — Last Two and Three Digits.")

        self.clear(self.rt(n, 0.1))
        nxt = self.label("NEXT VIDEO", color=self.GREY, size=26).move_to(UP * 2.6)
        topic = self.title_text("LAST TWO AND THREE DIGITS", color=self.YELLOW, size=50).next_to(nxt, DOWN, buff=0.3)
        two = VGroup(MathTex(r"\cdots", font_size=60, color=self.GREY),
                     *[self.digit_tile("?", self.YELLOW, side=0.8) for _ in range(2)]).arrange(RIGHT, buff=0.15)
        three = VGroup(MathTex(r"\cdots", font_size=60, color=self.GREY),
                       *[self.digit_tile("?", self.YELLOW, side=0.8) for _ in range(3)]).arrange(RIGHT, buff=0.15)
        VGroup(two, three).arrange(RIGHT, buff=1.4).move_to(DOWN * 0.7)
        self.play(FadeIn(nxt, shift=DOWN * 0.2), FadeIn(topic, scale=1.05), run_time=self.rt(n, 0.2))
        self.shine(topic, self.YELLOW, self.rt(n, 0.1))
        self.play(FadeIn(two, shift=UP * 0.2), run_time=self.rt(n, 0.12))
        self.play(FadeIn(three, shift=UP * 0.2), run_time=self.rt(n, 0.12))

        self.wait_for_narration(n)

        self.see_you_there()

        self.scene_end("done")