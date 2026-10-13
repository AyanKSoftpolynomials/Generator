from manim import *
from src.animation.lms_scene import LMSScene


class AssemblyLanguageVideo(LMSScene):
    """
    Assembly Language
    Module 5: Concepts of Programming | Day 13 | L1. Evaluation of Programming Languages
    Programming Language Fundamentals

    Visual concept:
        10110000   ──►   MOV A, 5        (binary row becomes a readable mnemonic)
        MOV A, 5   ──►  [ ASSEMBLER ]  ──►  10110000  ──►  CPU
        full sentence  ↔  shorthand   ==   binary  ↔  mnemonic

    Continuity with the previous lesson: the same CPU chip, bit rows,
    language stack and staircase. The translator box that was crossed out
    for machine language returns here as the ASSEMBLER.

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
    YELLOW = "#FFD54A"      # binary / machine code
    BLUE = "#4FC3F7"        # processor
    GREEN = "#69F0AE"       # mnemonics / assembly
    ORANGE = "#FFB74D"      # assembler (translator)
    RED = "#FF5252"
    PURPLE = "#B388FF"      # humans
    GREY = "#8A93A6"
    GRID = "#141A26"
    CHIP_FILL = "#0D1826"
    CARD_FILL = "#0F1A17"

    VOICE = "teacher_a"
    MONO = "Consolas"

    # illustrative encodings (shape of the idea, not a specific processor)
    PROGRAM = [
        ("10110000", "MOV", "A, 5", "move"),
        ("00000100", "ADD", "A, B", "add"),
        ("00101100", "SUB", "A, 1", "subtract"),
        ("11101011", "JMP", "LOOP", "jump"),
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

    # ---------- lesson-specific visuals ----------

    def chip(self, size=2.2):
        body = RoundedRectangle(corner_radius=0.15, width=size, height=size, stroke_color=self.BLUE,
                                stroke_width=3, fill_color=self.CHIP_FILL, fill_opacity=1)
        core = RoundedRectangle(corner_radius=0.08, width=size * 0.55, height=size * 0.55,
                                stroke_color=self.BLUE, stroke_width=2, fill_color=self.BLUE, fill_opacity=0.12)
        name = Text("CPU", font_size=int(size * 16), color=self.BLUE, weight=BOLD)
        pins = VGroup()
        for i in range(6):
            o = -size / 2 + size * (i + 0.5) / 6
            p = 0.18 * size / 2.2
            pins.add(Line([o, size / 2, 0], [o, size / 2 + p, 0]), Line([o, -size / 2, 0], [o, -size / 2 - p, 0]),
                     Line([size / 2, o, 0], [size / 2 + p, o, 0]), Line([-size / 2, o, 0], [-size / 2 - p, o, 0]))
        pins.set_stroke(self.BLUE, 3)
        return VGroup(pins, body, core, name)

    def pulse(self, cpu):
        return AnimationGroup(Indicate(cpu[2], color=self.YELLOW, scale_factor=1.15),
                              Flash(cpu, color=self.BLUE, flash_radius=cpu.width * 0.65, line_length=0.3))

    def bit_row(self, bits, cell=0.42):
        row = VGroup()
        for b in bits:
            on = b == "1"
            sq = Square(side_length=cell, stroke_color=self.YELLOW if on else self.GREY, stroke_width=2,
                        fill_color=self.YELLOW, fill_opacity=0.85 if on else 0)
            d = Text(b, font_size=int(cell * 60), color=self.BG if on else self.GREY, weight=BOLD).move_to(sq)
            row.add(VGroup(sq, d))
        return row.arrange(RIGHT, buff=0.04)

    def mnemonic(self, op, args, width=3.0, size=32):
        """A readable instruction card: opcode (green) + operands (white)."""
        text = VGroup(Text(op, font=self.MONO, font_size=size, color=self.GREEN, weight=BOLD),
                      Text(args, font=self.MONO, font_size=size, color=self.WHITE)).arrange(RIGHT, buff=0.25)
        box = RoundedRectangle(corner_radius=0.12, width=width, height=text.height + 0.35,
                               stroke_color=self.GREEN, stroke_width=2.5, fill_color=self.CARD_FILL, fill_opacity=1)
        text.move_to(box)
        return VGroup(box, text)

    def gear(self, radius=0.4, color=None):
        c = color or self.ORANGE
        teeth = VGroup(*[
            Rectangle(width=radius * 0.35, height=radius * 0.35, stroke_width=0, fill_color=c, fill_opacity=1)
            .move_to(UP * radius).rotate(a, about_point=ORIGIN)
            for a in np.arange(0, TAU, TAU / 8)
        ])
        rim = Circle(radius=radius * 0.85, stroke_color=c, stroke_width=5, fill_color=c, fill_opacity=0.25)
        hub = Circle(radius=radius * 0.3, stroke_color=c, stroke_width=4)
        return VGroup(teeth, rim, hub)

    def assembler(self, width=2.6, height=1.6):
        box = RoundedRectangle(corner_radius=0.18, width=width, height=height, stroke_color=self.ORANGE,
                               stroke_width=3, fill_color=self.ORANGE, fill_opacity=0.1)
        g = self.gear(radius=height * 0.24).move_to(box.get_center() + UP * height * 0.12)
        name = Text("ASSEMBLER", font_size=int(height * 16), color=self.ORANGE, weight=BOLD)
        name.move_to(box.get_bottom() + UP * height * 0.2)
        a = VGroup(box, g, name)
        a.gear_part = g
        return a

    def layer(self, text, color, width, y, extra=None, dashed=False):
        box = RoundedRectangle(corner_radius=0.15, width=width, height=0.8, stroke_color=color, stroke_width=3,
                               fill_color=color, fill_opacity=0 if dashed else 0.15)
        if dashed:
            box = DashedVMobject(box, num_dashes=50)
        content = self.label(text, color=color, size=24, weight=BOLD)
        if extra is not None:
            content = VGroup(content, extra).arrange(RIGHT, buff=0.35)
        g = VGroup(box, content.move_to(box))
        return g.move_to([0, y, 0])

    def step(self, text, color, center, dashed=False, width=3.4):
        box = RoundedRectangle(corner_radius=0.1, width=width, height=0.9, stroke_color=color, stroke_width=3,
                               fill_color=color, fill_opacity=0 if dashed else 0.2)
        if dashed:
            box = DashedVMobject(box, num_dashes=40)
        content = (Text("?", font_size=52, color=self.YELLOW, weight=BOLD) if text == "?"
                   else self.label(text, color=color, size=22, weight=BOLD))
        return VGroup(box, content.move_to(box)).move_to(center)

    # =========================================================
    # 1. HOOK
    # =========================================================

    def hook(self):

        self.scene_start("hook")

        n = self.say(
            "hook_01",
            "What if, instead of raw 0s and 1s, we used short, memorable abbreviations "
            "to represent the very same instructions?",
        )

        codes = ["10110000", "00000100", "00101100", "11101011", "01001000", "10010011"]
        wall = VGroup(*[self.bit_row(c, cell=0.38) for c in codes]).arrange(DOWN, buff=0.2).move_to([-2.2, 0.2, 0])
        self.play(LaggedStart(*[FadeIn(r, shift=DOWN * 0.15) for r in wall], lag_ratio=0.15),
                  run_time=self.rt(n, 0.25))
        # raw binary is hard on human eyes
        self.play(wall.animate.set_opacity(0.45), run_time=self.rt(n, 0.1))
        self.play(wall[0].animate.set_opacity(1), run_time=self.rt(n, 0.08))

        tag = self.mnemonic("MOV", "A, 5", width=2.8).move_to([3.4, wall[0].get_y(), 0])
        arrow = Arrow(wall[0].get_right(), tag.get_left(), buff=0.25, color=self.GREEN, stroke_width=4)
        self.play(GrowArrow(arrow), FadeIn(tag, shift=LEFT * 0.2), run_time=self.rt(n, 0.2))
        self.shine(tag[0], self.GREEN, self.rt(n, 0.08))
        what_if = Text("?", font_size=90, color=self.YELLOW, weight=BOLD).next_to(tag, DOWN, buff=0.5)
        self.play(Write(what_if), run_time=self.rt(n, 0.1))

        self.wait_for_narration(n)

    # =========================================================
    # 2. INTRODUCTION
    # =========================================================

    def introduction(self):

        self.scene_start("introduction")

        # -----------------------------------------------------
        # Narration 1
        # -----------------------------------------------------

        n = self.say("intro_01", "Hello again, my dear students.")

        self.clear(self.rt(n, 0.2))
        greeting = self.title_text("Hello again, my dear students.", color=self.YELLOW, size=46)
        self.play(FadeIn(greeting, shift=UP * 0.3), run_time=self.rt(n, 0.35))
        halo = self.shine(greeting, self.YELLOW, self.rt(n, 0.2))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — one step up the staircase
        # -----------------------------------------------------

        n = self.say("intro_02", "Today, assembly language, a small but meaningful step up from raw machine code.")

        self.play(FadeOut(greeting, halo), run_time=self.rt(n, 0.08))

        title = self.title_text("ASSEMBLY LANGUAGE", color=self.GREEN, size=62).move_to(UP * 2.5)
        sub = self.label("a small but meaningful step up", color=self.GREY, size=28).next_to(title, DOWN, buff=0.3)
        step1 = self.step("MACHINE LANGUAGE", self.YELLOW, [-3.2, -2.3, 0])
        step2 = self.step("ASSEMBLY LANGUAGE", self.GREEN, [0.6, -1.2, 0])
        climber = self.person(self.PURPLE).scale(0.45).next_to(step1, UP, buff=0.02)

        self.play(FadeIn(title, scale=1.1), run_time=self.rt(n, 0.12))
        self.shine(title, self.GREEN, self.rt(n, 0.08))
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=self.rt(n, 0.08))
        self.play(FadeIn(step1, shift=UP * 0.2), FadeIn(climber), run_time=self.rt(n, 0.12))
        self.play(FadeIn(step2, shift=UP * 0.2), run_time=self.rt(n, 0.1))
        self.play(climber.animate(path_arc=-PI / 2).next_to(step2, UP, buff=0.02), run_time=self.rt(n, 0.15))
        self.sweep(step2, self.GREEN, self.rt(n, 0.1), buff=0.08)

        self.wait_for_narration(n)

    # =========================================================
    # 3. HOW
    # =========================================================

    def how(self):

        self.scene_start("how")

        # -----------------------------------------------------
        # Narration 1 — binary rows become mnemonics
        # -----------------------------------------------------

        n = self.say(
            "how_01",
            "Assembly language replaces binary instructions with short, human-readable "
            "abbreviations called mnemonics,",
        )

        self.clear(self.rt(n, 0.08))

        ys = [1.6, 0.6, -0.4, -1.4]
        rows = VGroup(*[self.bit_row(bits).move_to([-3.6, y, 0]) for (bits, _, _, _), y in zip(self.PROGRAM, ys)])
        cards = VGroup(*[self.mnemonic(op, args).move_to([2.6, y, 0]) for (_, op, args, _), y in zip(self.PROGRAM, ys)])
        arrows = VGroup(*[Arrow(r.get_right(), c.get_left(), buff=0.25, color=self.GREY, stroke_width=3)
                          for r, c in zip(rows, cards)])
        meanings = VGroup(*[self.label(word, color=self.GREY, size=22).next_to(c, RIGHT, buff=0.3)
                            for (_, _, _, word), c in zip(self.PROGRAM, cards)])

        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.15), run_time=self.rt(n, 0.15))
        self.play(LaggedStart(*[AnimationGroup(GrowArrow(a), TransformFromCopy(r, c))
                                for a, r, c in zip(arrows, rows, cards)], lag_ratio=0.25),
                  run_time=self.rt(n, 0.3))
        # a mnemonic is an abbreviation of what the instruction does
        self.play(LaggedStart(*[FadeIn(m, shift=LEFT * 0.1) for m in meanings], lag_ratio=0.2),
                  run_time=self.rt(n, 0.15))
        brace = Brace(cards, UP, buff=0.15, color=self.GREEN)
        brace_lbl = self.label("mnemonics", color=self.GREEN, size=26, weight=BOLD).next_to(brace, UP, buff=0.1)
        self.play(GrowFromCenter(brace), FadeIn(brace_lbl), run_time=self.rt(n, 0.1))
        note = self.label("illustrative encodings", color=self.GREY, size=18).to_corner(DR, buff=0.3)
        self.play(FadeIn(note), run_time=self.rt(n, 0.05))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — the assembler translates them back
        # -----------------------------------------------------

        n = self.say("how_02", "which are then translated into machine language by a program called an assembler.")

        y = 0.2
        self.code_stack = cards.copy()
        self.code_stack.scale(0.8).arrange(DOWN, buff=0.12).move_to([-4.9, y, 0])
        self.play(FadeOut(rows, arrows, meanings, brace, brace_lbl),
                  ReplacementTransform(cards, self.code_stack), run_time=self.rt(n, 0.15))

        self.asm = self.assembler().move_to([-1.3, y, 0])
        self.machine_code = VGroup(*[self.bit_row(bits, cell=0.3) for bits, _, _, _ in self.PROGRAM])
        self.machine_code.arrange(DOWN, buff=0.14).move_to([2.0, y, 0])
        self.cpu = self.chip(size=1.6).move_to([5.3, y, 0])
        self.pipe = VGroup(
            Arrow(self.code_stack.get_right(), self.asm.get_left(), buff=0.12, color=self.GREY, stroke_width=3),
            Arrow(self.asm.get_right(), self.machine_code.get_left(), buff=0.15, color=self.GREY, stroke_width=3),
            Arrow(self.machine_code.get_right(), self.cpu.get_left(), buff=0.3, color=self.GREY, stroke_width=3),
        )
        self.play(FadeIn(self.asm, scale=0.9), GrowArrow(self.pipe[0]), run_time=self.rt(n, 0.12))
        self.play(FadeIn(self.cpu), run_time=self.rt(n, 0.08))

        # the cards feed the assembler, its gear turns, binary comes out
        feed = [c.copy() for c in self.code_stack]
        self.play(
            LaggedStart(*[f.animate.move_to(self.asm).scale(0.2).set_opacity(0) for f in feed], lag_ratio=0.2),
            Rotate(self.asm.gear_part, angle=-TAU, about_point=self.asm.gear_part.get_center()),
            run_time=self.rt(n, 0.2),
        )
        self.play(GrowArrow(self.pipe[1]),
                  LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in self.machine_code], lag_ratio=0.2),
                  run_time=self.rt(n, 0.15))
        self.play(GrowArrow(self.pipe[2]), run_time=self.rt(n, 0.06))
        self.play(self.pulse(self.cpu), run_time=self.rt(n, 0.1))

        self.wait_for_narration(n)

    # =========================================================
    # 4. WHAT
    # =========================================================

    def what(self):

        self.scene_start("what")

        n = self.say(
            "what_01",
            "Assembly language uses short, human-readable mnemonics instead of raw binary, "
            "translated by an assembler.",
        )

        title = self.title_text("ASSEMBLY LANGUAGE", color=self.GREEN, size=46).to_edge(UP, buff=0.4)
        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=self.rt(n, 0.1))
        self.shine(title, self.GREEN, self.rt(n, 0.07))

        def caption(mob, head, sub, color):
            g = VGroup(self.label(head, color=color, size=22, weight=BOLD),
                       self.label(sub, color=self.GREY, size=18)).arrange(DOWN, buff=0.08)
            return g.next_to(mob, DOWN, buff=0.35)

        c_code = caption(self.code_stack, "MNEMONICS", "human-readable", self.GREEN)
        c_asm = caption(self.asm, "TRANSLATOR", "the assembler", self.ORANGE)
        c_bin = caption(self.machine_code, "MACHINE CODE", "raw binary", self.YELLOW)
        c_cpu = caption(self.cpu, "EXECUTES", "the processor", self.BLUE)
        c_bin.align_to(c_code, UP)
        c_asm.align_to(c_code, UP)
        c_cpu.align_to(c_code, UP)

        self.play(FadeIn(c_code, shift=UP * 0.15), self.code_stack.animate.set_opacity(1), run_time=self.rt(n, 0.12))
        self.sweep(self.code_stack, self.GREEN, self.rt(n, 0.1))
        self.play(FadeIn(c_bin, shift=UP * 0.15), run_time=self.rt(n, 0.1))
        self.play(FadeIn(c_asm, shift=UP * 0.15),
                  Rotate(self.asm.gear_part, angle=-TAU, about_point=self.asm.gear_part.get_center()),
                  run_time=self.rt(n, 0.15))
        self.sweep(self.asm, self.ORANGE, self.rt(n, 0.1))
        self.play(FadeIn(c_cpu, shift=UP * 0.15), self.pulse(self.cpu), run_time=self.rt(n, 0.1))

        self.wait_for_narration(n)

    # =========================================================
    # 5. WHY
    # =========================================================

    def why(self):

        self.scene_start("why")

        # -----------------------------------------------------
        # Narration 1 — manageable for humans
        # -----------------------------------------------------

        n = self.say(
            "why_01",
            "This matters because assembly language made programming genuinely more manageable for humans,",
        )

        self.clear(self.rt(n, 0.12))

        cpu = self.chip(size=1.3).move_to([0, -2.75, 0])
        machine = self.layer("MACHINE LANGUAGE", self.YELLOW, 7.0, -1.35, extra=self.bit_row("1011", cell=0.28))
        machine.set_opacity(0.55)
        assembly = self.layer("ASSEMBLY", self.GREEN, 6.2, -0.25,
                              extra=Text("MOV A, 5", font=self.MONO, font_size=24, color=self.WHITE))
        future = self.layer("· · ·", self.GREY, 5.2, 0.85, dashed=True)

        self.play(FadeIn(cpu), FadeIn(machine, shift=UP * 0.2), run_time=self.rt(n, 0.15))
        self.play(FadeIn(assembly, shift=UP * 0.2), run_time=self.rt(n, 0.12))
        self.shine(assembly[0], self.GREEN, self.rt(n, 0.08))
        self.play(FadeIn(future), run_time=self.rt(n, 0.08))

        human = self.person(self.PURPLE).scale(0.55).move_to([-5.6, -0.1, 0])
        reads = Arrow(human.get_right(), assembly.get_left(), buff=0.2, color=self.PURPLE, stroke_width=4)
        reads_lbl = self.label("readable", color=self.PURPLE, size=22).next_to(reads, UP, buff=0.1)
        self.play(FadeIn(human, shift=RIGHT * 0.2), run_time=self.rt(n, 0.1))
        self.play(GrowArrow(reads), FadeIn(reads_lbl), run_time=self.rt(n, 0.12))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — still close to the hardware
        # -----------------------------------------------------

        n = self.say("why_02", "while still staying very close to the hardware itself.")

        path = VGroup(Line(assembly.get_bottom(), machine.get_top()), Line(machine.get_bottom(), cpu.get_top()))
        path.set_stroke(self.GREEN, 5)
        self.play(Create(path), run_time=self.rt(n, 0.15))
        self.play(ShowPassingFlash(path.copy().set_stroke(self.YELLOW, 10), time_width=0.7),
                  self.pulse(cpu), run_time=self.rt(n, 0.2))

        brace = Brace(VGroup(assembly, machine, cpu), RIGHT, buff=0.3, color=self.GREEN)
        close = self.label("very close to\nthe hardware", color=self.GREEN, size=24, weight=BOLD)
        close.next_to(brace, RIGHT, buff=0.15)
        self.play(GrowFromCenter(brace), FadeIn(close, shift=LEFT * 0.2), run_time=self.rt(n, 0.2))
        self.shine(close, self.GREEN, self.rt(n, 0.1))

        self.wait_for_narration(n)

    # =========================================================
    # 6. REAL WORLD EXAMPLE
    # =========================================================

    def real_world_example(self):

        self.scene_start("real_world")

        # -----------------------------------------------------
        # Narration 1 — shorthand stays tied to the sentence
        # -----------------------------------------------------

        n = self.say("example_01", "Think of shorthand notes, still closely tied to the full sentence,")

        full_words = ["Meeting", "with", "the team", "at", "three o'clock", "tomorrow"]
        short_words = ["Mtg", "w/", "team", "@", "3", "tmrw"]
        full = VGroup(*[self.label(w, size=32) for w in full_words]).arrange(RIGHT, buff=0.28).move_to([0, 1.6, 0])
        heading = self.label("NOTES", color=self.GREY, size=22, weight=BOLD).next_to(full, UP, buff=0.5).align_to(full, LEFT)

        self.slide_board(VGroup(heading), LEFT, self.rt(n, 0.15))
        self.play(Write(full), run_time=self.rt(n, 0.3))

        short = VGroup(*[
            Text(s, font_size=34, color=self.GREEN, slant=ITALIC, weight=BOLD).move_to([w.get_x(), 0.2, 0])
            for s, w in zip(short_words, full)
        ])
        ties = VGroup(*[DashedLine(w.get_bottom() + DOWN * 0.1, s.get_top() + UP * 0.1, color=self.GREY,
                                   stroke_width=2) for w, s in zip(full, short)])
        self.play(LaggedStart(*[AnimationGroup(Create(t), FadeIn(s, shift=DOWN * 0.15))
                                for t, s in zip(ties, short)], lag_ratio=0.15), run_time=self.rt(n, 0.3))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — quicker and easier to write
        # -----------------------------------------------------

        n = self.say("example_02", "but noticeably quicker and easier to write.")

        compact = short.copy().arrange(RIGHT, buff=0.22).move_to([0, 0.2, 0])
        self.play(FadeOut(ties), Transform(short, compact), run_time=self.rt(n, 0.15))

        bar_full = Rectangle(width=full.width, height=0.35, stroke_width=0, fill_color=self.GREY,
                             fill_opacity=0.6).move_to([0, -1.2, 0]).align_to(full, LEFT)
        bar_short = Rectangle(width=short.width, height=0.35, stroke_width=0, fill_color=self.GREEN,
                              fill_opacity=0.85).move_to([0, -1.8, 0]).align_to(full, LEFT)
        lbl_full = self.label("full sentence", color=self.GREY, size=20).next_to(bar_full, LEFT, buff=0.2)
        lbl_short = self.label("shorthand", color=self.GREEN, size=20).next_to(bar_short, LEFT, buff=0.2)
        VGroup(lbl_full, lbl_short).align_to(lbl_full, RIGHT)
        self.play(GrowFromEdge(bar_full, LEFT), FadeIn(lbl_full), run_time=self.rt(n, 0.12))
        self.play(GrowFromEdge(bar_short, LEFT), FadeIn(lbl_short), run_time=self.rt(n, 0.12))
        quick = VGroup(self.check_mark(self.GREEN), self.label("quicker", color=self.GREEN, size=24, weight=BOLD))
        quick.arrange(RIGHT, buff=0.15).next_to(bar_short, RIGHT, buff=0.3)
        self.play(FadeIn(quick, shift=LEFT * 0.2), run_time=self.rt(n, 0.1))

        # the parallel: shorthand is to a sentence what a mnemonic is to binary
        parallel = VGroup(
            self.label("shorthand", color=self.GREEN, size=26, weight=BOLD),
            self.label("↔ sentence", color=self.WHITE, size=26),
            self.label("  =  ", color=self.GREY, size=26),
            Text("MOV A, 5", font=self.MONO, font_size=26, color=self.GREEN, weight=BOLD),
            self.label("↔", color=self.WHITE, size=26),
            self.bit_row("10110000", cell=0.3),
        ).arrange(RIGHT, buff=0.2).move_to([0, -3.0, 0])
        self.play(FadeIn(parallel, shift=UP * 0.2), run_time=self.rt(n, 0.15))
        self.sweep(parallel, self.YELLOW, self.rt(n, 0.1), buff=0.12)

        self.wait_for_narration(n)

    # =========================================================
    # 7. SUMMARY
    # =========================================================

    def summary(self):

        self.scene_start("summary")

        n = self.say(
            "summary_01",
            "In short, assembly language uses readable mnemonics instead of binary, "
            "translated by an assembler into machine code.",
        )

        summary_title = self.title_text("THE TAKEAWAY", color=self.YELLOW, size=50).to_edge(UP, buff=0.5)
        card = self.mnemonic("MOV", "A, 5", width=2.6, size=28).move_to([-4.6, 1.1, 0])
        asm = self.assembler(width=2.0, height=1.2).move_to([-1.3, 1.1, 0])
        bits = self.bit_row("10110000", cell=0.32).move_to([2.1, 1.1, 0])
        cpu = self.chip(size=1.1).move_to([5.4, 1.1, 0])
        arrows = VGroup(
            Arrow(card.get_right(), asm.get_left(), buff=0.12, color=self.GREY, stroke_width=3),
            Arrow(asm.get_right(), bits.get_left(), buff=0.15, color=self.GREY, stroke_width=3),
            Arrow(bits.get_right(), cpu.get_left(), buff=0.25, color=self.GREY, stroke_width=3),
        )

        self.slide_board(VGroup(summary_title), UP, self.rt(n, 0.12))
        self.shine(summary_title, self.YELLOW, self.rt(n, 0.05))
        self.play(FadeIn(card, shift=RIGHT * 0.2), run_time=self.rt(n, 0.08))
        self.play(GrowArrow(arrows[0]), FadeIn(asm), run_time=self.rt(n, 0.08))
        self.play(Rotate(asm.gear_part, angle=-TAU, about_point=asm.gear_part.get_center()),
                  GrowArrow(arrows[1]), FadeIn(bits, shift=RIGHT * 0.2), run_time=self.rt(n, 0.1))
        self.play(GrowArrow(arrows[2]), FadeIn(cpu), run_time=self.rt(n, 0.07))

        points = VGroup(*[
            VGroup(self.check_mark(self.GREEN), self.label(text, size=30)).arrange(RIGHT, buff=0.3)
            for text in ["readable mnemonics instead of binary", "translated by an assembler", "into machine code"]
        ]).arrange(DOWN, buff=0.45, aligned_edge=LEFT).move_to(DOWN * 1.7)

        self.play(FadeIn(points[0], shift=RIGHT * 0.2), Indicate(card, color=self.GREEN), run_time=self.rt(n, 0.12))
        self.play(FadeIn(points[1], shift=RIGHT * 0.2), Indicate(asm, color=self.ORANGE), run_time=self.rt(n, 0.12))
        self.play(FadeIn(points[2], shift=RIGHT * 0.2), Indicate(bits, color=self.YELLOW), self.pulse(cpu),
                  run_time=self.rt(n, 0.12))

        self.wait_for_narration(n)

    # =========================================================
    # 8. DONE
    # =========================================================

    def done(self):

        self.scene_start("done")

        n = self.say("done_01", "With assembly clear, let's meet the level most programmers actually use today.")

        self.clear(self.rt(n, 0.1))

        step1 = self.step("MACHINE LANGUAGE", self.YELLOW, [-4.2, -2.6, 0])
        step2 = self.step("ASSEMBLY LANGUAGE", self.GREEN, [-0.6, -1.5, 0])
        step3 = self.step("?", self.GREY, [3.0, -0.4, 0], dashed=True)
        climber = self.person(self.PURPLE).scale(0.45).next_to(step2, UP, buff=0.02)

        self.play(FadeIn(step1, shift=UP * 0.2), FadeIn(step2, shift=UP * 0.2), FadeIn(climber),
                  run_time=self.rt(n, 0.15))
        self.play(Create(step3[0]), Write(step3[1]), run_time=self.rt(n, 0.12))
        self.shine(step3[1], self.YELLOW, self.rt(n, 0.06))

        # the next level is where most programmers work
        crowd = VGroup(*[self.person(c).scale(0.3) for c in [self.BLUE, self.ORANGE, self.GREEN, self.PURPLE]])
        crowd.arrange(RIGHT, buff=0.25).next_to(step3, UP, buff=0.02).shift(RIGHT * 0.5)
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.3) for p in crowd], lag_ratio=0.15), run_time=self.rt(n, 0.15))
        target = climber.copy().next_to(step3, UP, buff=0.02).next_to(crowd, LEFT, buff=0.25)
        target.align_to(crowd, DOWN)
        self.play(climber.animate(path_arc=-PI / 2).move_to(target), run_time=self.rt(n, 0.17))
        most = self.label("most programmers today", color=self.GREY, size=22).next_to(step3, DOWN, buff=0.3)
        self.play(FadeIn(most), run_time=self.rt(n, 0.08))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Final narration
        # -----------------------------------------------------

        n = self.say("done_02", "I will see you in the next video.")

        see_you = self.title_text("SEE YOU IN THE NEXT VIDEO!", color=self.YELLOW, size=48).move_to(UP * 2.5)
        self.play(FadeIn(see_you, scale=1.1), run_time=self.rt(n, 0.4))
        self.shine(see_you, self.YELLOW, self.rt(n, 0.25))

        self.wait_for_narration(n)

        self.clear(0.8)

        self.scene_end("done")