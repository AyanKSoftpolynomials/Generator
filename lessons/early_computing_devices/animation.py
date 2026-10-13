"""
Computer Fundamentals > Evolution and Types of Computers >
Evolution of Computers > Early Computing Devices to the First Electronic Computers

One narrated LMSScene. Each lesson section is a scene_start()/scene_end()
block; the visuals wait on the narration audio, so no timings are hard-coded.

    python generate.py lessons/early_computing_devices/animation.py
"""

import numpy as np
from manim import *

from src.animation import LMSScene

# ---------------------------------------------------------------- style ----

BG = "#0F172A"
FONT = "Segoe UI"
INK = "#E2E8F0"
MUTED = "#94A3B8"
PANEL = "#1E293B"
GOOD = "#34D399"
BAD = "#F87171"
GOLD = "#FBBF24"

PHASES = [
    ("Manual", "#F59E0B"),
    ("Mechanical", "#14B8A6"),
    ("Electromechanical", "#A78BFA"),
    ("Electronic", "#60A5FA"),
]
MANUAL, MECH, ELMECH, ELEC = (c for _, c in PHASES)


def T(text, size=32, color=INK, weight=NORMAL, **kw):
    return Text(text, font=FONT, font_size=size, color=color, weight=weight, **kw)


def fit(mob, max_width):
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    return mob


# ---------------------------------------------------------------- icons ----

def abacus_icon():
    frame = Rectangle(width=2.4, height=1.6, stroke_color="#B45309", stroke_width=6)
    rods, beads = VGroup(), VGroup()
    for i in range(4):
        y = 0.55 - i * 0.37
        rods.add(Line([-1.2, y, 0], [1.2, y, 0], stroke_color=MUTED, stroke_width=2))
        for j in range(2 + (i * 2) % 4):
            beads.add(Circle(radius=0.12, fill_color=MANUAL, fill_opacity=1, stroke_width=0)
                      .move_to([-0.95 + j * 0.27, y, 0]))
    return VGroup(frame, rods, beads)


def napier_icon():
    rods = VGroup()
    for k in range(4):
        body = RoundedRectangle(corner_radius=0.05, width=0.45, height=1.8,
                                fill_color="#FDE68A", fill_opacity=1, stroke_width=0)
        cells = VGroup(*[Line(LEFT * 0.18, RIGHT * 0.18, stroke_color="#78350F", stroke_width=3)
                         .move_to(body).shift(UP * y) for y in (0.45, 0, -0.45)])
        rods.add(VGroup(body, cells))
    return rods.arrange(RIGHT, buff=0.12)


def gear_icon(color, teeth=10, r=0.8):
    angles = np.linspace(0, TAU, teeth, endpoint=False)
    cogs = VGroup(*[Square(0.32, fill_color=color, fill_opacity=1, stroke_width=0)
                    .rotate(a).move_to([(r + 0.08) * np.cos(a), (r + 0.08) * np.sin(a), 0])
                    for a in angles])
    body = Circle(radius=r, fill_color=color, fill_opacity=1, stroke_width=0)
    hole = Circle(radius=r * 0.35, fill_color=PANEL, fill_opacity=1, stroke_width=0)
    return VGroup(cogs, body, hole)


def twin_gears(color):
    g1 = gear_icon(color)
    g2 = gear_icon(color, teeth=8, r=0.55).next_to(g1, RIGHT, buff=-0.05).shift(DOWN * 0.45)
    return VGroup(g1, g2)


def punch_card(pattern, width_per_cell=0.28):
    rows, cols = len(pattern), len(pattern[0])
    base = RoundedRectangle(corner_radius=0.06, width=cols * width_per_cell + 0.3,
                            height=rows * width_per_cell + 0.3,
                            fill_color="#F1E6C8", fill_opacity=1, stroke_width=0)
    holes = VGroup()
    for r, line in enumerate(pattern):
        for c, bit in enumerate(line):
            if bit == "1":
                holes.add(Dot(radius=0.07, color=BG).move_to(
                    base.get_corner(UL) + np.array([0.15 + (c + 0.5) * width_per_cell,
                                                    -0.15 - (r + 0.5) * width_per_cell, 0])))
    return VGroup(base, holes)


def weave(pattern, color):
    cells = VGroup()
    for line in pattern:
        for bit in line:
            cells.add(Square(0.34, stroke_width=1, stroke_color=BG,
                             fill_color=color if bit == "1" else "#334155", fill_opacity=1))
    return cells.arrange_in_grid(rows=len(pattern), cols=len(pattern[0]), buff=0)


def tube_icon():
    glass = RoundedRectangle(corner_radius=0.4, width=0.9, height=1.5,
                             stroke_color=INK, stroke_width=3, fill_color=GOLD, fill_opacity=0.15)
    filament = VMobject(stroke_color=GOLD, stroke_width=4).set_points_as_corners(
        [[-0.25, -0.3, 0], [-0.12, 0.25, 0], [0, -0.3, 0], [0.12, 0.25, 0], [0.25, -0.3, 0]])
    base = Rectangle(width=0.9, height=0.35, fill_color="#475569", fill_opacity=1,
                     stroke_width=0).next_to(glass, DOWN, buff=0)
    pins = VGroup(*[Line(UP * 0, DOWN * 0.3, stroke_color=MUTED, stroke_width=3).shift(RIGHT * x)
                    for x in (-0.25, 0, 0.25)]).next_to(base, DOWN, buff=0)
    return VGroup(glass, filament, base, pins)


def bolt_icon(color):
    return Polygon([0.1, 0.6, 0], [-0.35, -0.05, 0], [-0.02, -0.05, 0], [-0.15, -0.6, 0],
                   [0.35, 0.1, 0], [0.02, 0.1, 0], fill_color=color, fill_opacity=1, stroke_width=0)


def relay_icon(color):
    return VGroup(gear_icon(color), bolt_icon(GOLD).scale(1.2).shift(RIGHT * 1.1 + UP * 0.3))


def block_icon(labels, color):
    boxes = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.08, width=1.0, height=0.6,
                                             stroke_color=color, stroke_width=3),
                            T(l, 16, color, BOLD)) for l in labels])
    return boxes.arrange(RIGHT, buff=0.18)


def person_icon(color=MUTED):
    head = Circle(radius=0.2, fill_color=color, fill_opacity=1, stroke_width=0)
    body = RoundedRectangle(corner_radius=0.15, width=0.6, height=0.6, fill_color=color,
                            fill_opacity=1, stroke_width=0).next_to(head, DOWN, buff=0.05)
    return VGroup(head, body)


def mainframe_icon(color):
    cab = RoundedRectangle(corner_radius=0.08, width=1.8, height=1.4, stroke_color=color, stroke_width=3)
    reels = VGroup(*[Circle(radius=0.28, stroke_color=color, stroke_width=3) for _ in range(2)])
    reels.arrange(RIGHT, buff=0.3).move_to(cab).shift(UP * 0.2)
    lights = VGroup(*[Dot(radius=0.05, color=GOLD) for _ in range(5)]).arrange(RIGHT, buff=0.12)
    lights.next_to(reels, DOWN, buff=0.2)
    return VGroup(cab, reels, lights)


# --------------------------------------------------------------- blocks ----

def card(name, year, tag, color, icon, w=3.8, h=3.1):
    box = RoundedRectangle(corner_radius=0.18, width=w, height=h, stroke_color=color,
                           stroke_width=3, fill_color=PANEL, fill_opacity=1)
    icon.scale_to_fit_height(0.95)
    fit(icon, w - 0.8)
    title = fit(T(name, 28, INK, BOLD), w - 0.4)
    yr = T(year, 22, color, BOLD)
    tg = fit(T(tag, 20, MUTED), w - 0.4)
    content = VGroup(icon, title, yr, tg).arrange(DOWN, buff=0.14).move_to(box)
    return VGroup(box, content)


def timeline(width=13.0, h=0.62):
    w = width / 4
    bands = VGroup()
    for name, col in PHASES:
        rect = RoundedRectangle(corner_radius=0.08, width=w - 0.08, height=h,
                                stroke_width=0, fill_color=col, fill_opacity=0.22)
        lab = fit(T(name, 22, col, BOLD), w - 0.3)
        bands.add(VGroup(rect, lab.move_to(rect)))
    return bands.arrange(RIGHT, buff=0.08)


def focus_band(bands, index):
    anims = []
    for i, (rect, lab) in enumerate(bands):
        col = PHASES[i][1]
        on = i == index
        anims.append(rect.animate.set_fill(col, opacity=0.95 if on else 0.12))
        anims.append(lab.animate.set_color(BG if on else col))
    return AnimationGroup(*anims)


def header_left():
    return T("COMPUTER FUNDAMENTALS  ·  EVOLUTION OF COMPUTERS", 16, MUTED).to_corner(UL, buff=0.3)


def header_right(section):
    return T(section.upper(), 16, GOLD, BOLD).to_corner(UR, buff=0.3)


def option_row(letter, text, width=11.0):
    box = RoundedRectangle(corner_radius=0.12, width=width, height=0.72,
                           stroke_color=MUTED, stroke_width=2, fill_color=PANEL, fill_opacity=1)
    badge = VGroup(Circle(radius=0.24, stroke_color=GOLD, stroke_width=2.5),
                   T(letter, 22, GOLD, BOLD))
    badge.move_to(box.get_left() + RIGHT * 0.45)
    lab = fit(T(text, 24, INK), width - 1.3)
    lab.next_to(badge, RIGHT, buff=0.3)
    return VGroup(box, badge, lab)


def mcq(question, options):
    q = fit(T(question, 30, INK, BOLD, line_spacing=0.9), 12.5)
    rows = VGroup(*[option_row(l, t) for l, t in options]).arrange(DOWN, buff=0.2)
    return VGroup(q, rows).arrange(DOWN, buff=0.45)


def tag_inside(row, text):
    tag = T(text, 20, BAD)
    return tag.move_to(row[0].get_right() + LEFT * (tag.width / 2 + 0.3))


def strike(row):
    line = Line(row[0].get_left() + RIGHT * 0.2, row[0].get_right() + LEFT * 0.2,
                stroke_color=BAD, stroke_width=4)
    return AnimationGroup(row.animate.set_opacity(0.35), Create(line)), line


def mark_correct(row):
    return AnimationGroup(row[0].animate.set_stroke(GOOD, width=4).set_fill(GOOD, opacity=0.18),
                          Indicate(row[2], color=GOOD, scale_factor=1.06))


# ---------------------------------------------------------------- lesson ----

class EarlyComputingDevicesVideo(LMSScene):
    lesson_title = "Early Computing Devices to the First Electronic Computers"

    def construct(self):
        self.camera.background_color = BG
        self.head_left = header_left()
        self.head_right = None
        self.add(self.head_left)

        self.hook()
        self.concept_introduction()
        self.explanation()
        self.example()
        self.exam_application()
        self.common_mistakes()
        self.practice_question()
        self.answer_explanation()
        self.quick_revision()
        self.closing()

    # -- section helpers -----------------------------------------------------

    def begin(self, scene_id, title):
        self.scene_start(scene_id, title=title)
        new = header_right(title)
        if self.head_right is None:
            self.play(FadeIn(self.head_left), FadeIn(new), run_time=0.5)
        else:
            self.play(FadeOut(self.head_right), FadeIn(new), run_time=0.5)
        self.head_right = new

    def end(self):
        """Let the narration finish, then clear everything except the header."""
        self.wait_for_narration()
        keep = {self.head_left, self.head_right}
        others = [m for m in self.mobjects if m not in keep]
        if others:
            self.play(FadeOut(Group(*others)), run_time=0.7)
        self.scene_end()

    def say(self, id, text, **kw):
        return self.narrate(id, text, **kw)

    # -- S01 -----------------------------------------------------------------

    def hook(self):
        self.begin("S01_Hook", "Opening Hook")

        word = T("“computer”", 72, GOLD, BOLD)
        year = T("first recorded use: 1613", 30, MUTED).next_to(word, DOWN, buff=0.3)
        self.say("hook_1", "Here is a surprising fact. The word computer was first recorded in the year "
                           "sixteen thirteen, and back then it did not mean a machine at all.")
        self.play(AddTextLetterByLetter(word), run_time=1.5)
        self.play(FadeIn(year, shift=UP * 0.2))

        meaning = T("= a person whose job was to compute", 34, INK).next_to(year, DOWN, buff=0.5)
        self.say("hook_2", "A computer was a person, someone whose job was to compute.")
        self.play(Write(meaning))
        self.wait_for_narration()
        self.play(FadeOut(VGroup(word, year, meaning)))

        rng = np.random.default_rng(7)
        desks = VGroup()
        for _ in range(4):
            person = person_icon()
            desk = Line(LEFT * 0.8, RIGHT * 0.8, stroke_color="#B45309", stroke_width=6)
            desk.next_to(person, DOWN, buff=0.05)
            paper = VGroup(*[T(" ".join(str(d) for d in rng.integers(0, 10, 4)), 18, INK)
                             for _ in range(4)]).arrange(DOWN, buff=0.08)
            paper.next_to(person, UP, buff=0.25)
            desks.add(VGroup(person, desk, paper))
        desks.arrange(RIGHT, buff=1.0).shift(UP * 0.4)
        self.say("hook_3", "Rooms full of human computers worked through long columns of numbers by hand, "
                           "for tables used in navigation, astronomy and engineering.")
        self.play(LaggedStart(*[FadeIn(d, shift=UP * 0.3) for d in desks], lag_ratio=0.2))
        for _ in range(3):
            self.play(*[Indicate(d[2], color=GOLD, scale_factor=1.04) for d in desks], run_time=1)

        human = VGroup(person_icon(INK).scale(0.7), T("Human doing\narithmetic", 24, INK))
        human.arrange(DOWN, buff=0.2)
        machine = VGroup(gear_icon(GOLD, r=0.4), T("Machine running\ninstructions", 24, INK))
        machine.arrange(DOWN, buff=0.2)
        journey = VGroup(human, machine).arrange(RIGHT, buff=4.0).shift(DOWN * 2.2)
        arrow = Arrow(human.get_right(), machine.get_left(), buff=0.3, color=GOLD, stroke_width=6)
        q = T("?", 48, GOLD, BOLD).next_to(arrow, UP, buff=0.1)
        self.say("hook_4", "So how did we go from a human doing arithmetic to a machine that runs its own "
                           "instructions? That journey is what this lesson is about.")
        self.play(FadeIn(human), desks.animate.set_opacity(0.3))
        self.play(GrowArrow(arrow), FadeIn(machine), FadeIn(q, scale=1.5))
        self.end()

    # -- S02 -----------------------------------------------------------------

    def concept_introduction(self):
        self.begin("S02_ConceptIntroduction", "Concept Introduction")

        steps = ["Helps you count", "Does the arithmetic", "Follows a program", "Stores its own program"]
        lines = [
            "First came devices that simply help you count.",
            "Then machines that do the arithmetic for you.",
            "Then machines that follow a program, a set of instructions given from outside.",
            "And finally, machines that store their own program in memory.",
        ]
        stairs = VGroup()
        for i, s in enumerate(steps):
            col = PHASES[i][1]
            block = RoundedRectangle(corner_radius=0.1, width=3.0, height=0.8 + i * 0.55,
                                     fill_color=col, fill_opacity=0.9, stroke_width=0)
            lab = fit(T(s, 22, BG, BOLD), 2.7).move_to(block.get_top() + DOWN * 0.4)
            stairs.add(VGroup(block, lab))
        stairs.arrange(RIGHT, buff=0.15, aligned_edge=DOWN).move_to(DOWN * 0.3)
        title = T("More and more work handed to the machine", 30, INK).to_edge(UP, buff=1.0)
        self.say("intro_1", "The history of computing is really a story of handing more and more work to the machine.")
        self.play(FadeIn(title))
        for i, (s, text) in enumerate(zip(stairs, lines)):
            self.say(f"intro_step_{i + 1}", text)
            self.play(GrowFromEdge(s, DOWN), run_time=0.8)
        self.wait_for_narration()

        self.play(FadeOut(title), FadeOut(stairs))
        bands = timeline().move_to(UP * 0.4)
        caption = T("Four phases — named after the technology inside the machine", 26, MUTED)
        caption.next_to(bands, DOWN, buff=0.4)
        self.say("intro_2", "We group this history into four phases: manual, mechanical, electromechanical "
                            "and electronic. Each phase is named after the technology inside the machine.")
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.3) for b in bands], lag_ratio=0.3))
        self.play(FadeIn(caption))
        self.wait_for_narration()

        why = T("Why this matters in C-CAT", 30, GOLD, BOLD).move_to(DOWN * 1.7)
        chips = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.3, width=3.6, height=0.7,
                                                 stroke_color=GOLD, stroke_width=2),
                                T(t, 24, INK)) for t in
                         ("Who built it?", "What could it do?", "Which was first?")])
        for c in chips:
            c[1].move_to(c[0])
        chips.arrange(RIGHT, buff=0.4).next_to(why, DOWN, buff=0.35)
        self.say("intro_3", "Why does this matter for C-CAT? Questions here ask who built a machine, "
                            "what it could do, and which one came first.")
        self.play(FadeIn(why))
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in chips], lag_ratio=0.4))
        self.wait_for_narration()
        self.say("intro_4", "Pay special attention to what each machine could do. That is where most marks are won or lost.")
        self.play(Indicate(chips[1], color=GOLD), run_time=1.5)
        self.end()

    # -- S03 -----------------------------------------------------------------

    def explanation(self):
        self.begin("S03_Explanation", "Explanation")

        bands = timeline().to_edge(UP, buff=0.8)
        stage = DOWN * 0.7
        self.play(FadeIn(bands))

        # Manual
        self.play(focus_band(bands, 0))
        abacus = card("Abacus", "thousands of years ago", "each rod = a place value", MANUAL, abacus_icon())
        napier = card("Napier's Bones", "1617", "multiplication → additions", MANUAL, napier_icon())
        row = VGroup(abacus, napier).arrange(RIGHT, buff=0.8).move_to(stage)
        note = T("The human does the thinking", 24, GOLD).next_to(row, DOWN, buff=0.3)
        self.say("exp_abacus", "We begin in the manual phase with the abacus, used for thousands of years. "
                               "Each rod stands for a place value, but the human does all the thinking.")
        self.play(FadeIn(abacus, shift=UP * 0.3))
        self.play(FadeIn(note))
        self.say("exp_napier", "In sixteen seventeen, John Napier introduced Napier's Bones, numbered rods "
                               "that turn multiplication into a series of simple additions.")
        self.play(FadeIn(napier, shift=UP * 0.3))
        slide = T("→ led to the slide rule (logarithms)", 24, MUTED).next_to(row, DOWN, buff=0.3)
        self.say("exp_slide", "Napier's work on logarithms also led to the slide rule.")
        self.play(Transform(note, slide))
        self.wait_for_narration()
        self.play(FadeOut(VGroup(row, note)))

        # Mechanical
        self.play(focus_band(bands, 1))
        pascal = card("Pascaline", "1642 · Blaise Pascal", "+  −  only", MECH, gear_icon(MECH))
        leib = card("Stepped Reckoner", "1673 · G. W. Leibniz", "+  −  ×  ÷", MECH, twin_gears(MECH))
        row = VGroup(pascal, leib).arrange(RIGHT, buff=0.8).move_to(stage)
        self.say("exp_pascal", "The mechanical phase uses gears. In sixteen forty-two, Blaise Pascal built the "
                               "Pascaline, a gear-driven calculator that could only add and subtract.")
        self.play(FadeIn(pascal, shift=UP * 0.3))
        self.play(Rotate(pascal[1][0], angle=TAU / 3), run_time=1.5)
        self.say("exp_leibniz", "In sixteen seventy-three, Gottfried Leibniz built the Stepped Reckoner. It could "
                                "add, subtract, multiply and divide: all four basic operations.")
        self.play(FadeIn(leib, shift=UP * 0.3))
        self.play(Circumscribe(leib[1][3], color=GOLD))
        self.wait_for_narration()
        self.play(FadeOut(row))

        # Jacquard loom
        p1 = ["101010", "010101", "101010", "010101", "101010", "010101"]
        p2 = ["111000", "110001", "100011", "000111", "001110", "011100"]
        loom_title = T("Jacquard's loom · 1801", 30, MECH, BOLD).move_to(UP * 1.6)
        c1 = punch_card(p1).move_to(LEFT * 3 + DOWN * 0.8)
        w1 = weave(p1, MECH).move_to(RIGHT * 3 + DOWN * 0.8)
        arrow = Arrow(c1.get_right(), w1.get_left(), buff=0.4, color=GOLD, stroke_width=6)
        self.say("exp_loom_1", "In eighteen hundred and one, Joseph Marie Jacquard built a weaving loom "
                               "controlled by punched cards. The holes decided the pattern in the cloth.")
        self.play(FadeIn(loom_title), FadeIn(c1), GrowArrow(arrow), FadeIn(w1))
        c2 = punch_card(p2).move_to(c1)
        w2 = weave(p2, MECH).move_to(w1)
        idea = T("Change the cards → change the output  =  a program", 26, GOLD).move_to(DOWN * 3.0)
        self.say("exp_loom_2", "Change the cards, and you change the output. That is the idea of a program.")
        self.play(Transform(c1, c2), Transform(w1, w2), run_time=1.5)
        self.play(Write(idea))
        self.wait_for_narration()
        self.play(FadeOut(VGroup(loom_title, c1, w1, arrow, idea)))

        # Babbage & Lovelace
        diff = card("Difference Engine", "1822 · Charles Babbage", "mathematical tables",
                    MECH, block_icon(["Δ", "Δ", "Δ"], MECH)).move_to(stage)
        self.say("exp_diff", "In eighteen twenty-two, Charles Babbage designed the Difference Engine "
                             "to calculate mathematical tables automatically.")
        self.play(FadeIn(diff, shift=UP * 0.3))
        self.wait_for_narration()
        self.play(FadeOut(diff))

        eng_title = T("Analytical Engine · 1830s (designed, never completed)", 28, MECH, BOLD)
        eng_title.move_to(UP * 1.7)

        def unit(label, sub, col):
            box = RoundedRectangle(corner_radius=0.15, width=2.6, height=1.3, stroke_color=col,
                                   stroke_width=3, fill_color=PANEL, fill_opacity=1)
            return VGroup(box, VGroup(fit(T(label, 26, INK, BOLD), 2.3), T(sub, 18, MUTED))
                          .arrange(DOWN, buff=0.1).move_to(box))

        cards_in = unit("Punched cards", "input", MANUAL)
        mill = unit("Mill", "does the calculation", MECH)
        printer = unit("Printer", "output", ELEC)
        store = unit("Store", "holds the numbers", ELMECH)
        flow = VGroup(cards_in, mill, printer).arrange(RIGHT, buff=1.1).move_to(DOWN * 0.1)
        store.next_to(mill, DOWN, buff=0.8)
        a1 = Arrow(cards_in.get_right(), mill.get_left(), buff=0.1, color=INK)
        a2 = Arrow(mill.get_right(), printer.get_left(), buff=0.1, color=INK)
        a3 = DoubleArrow(mill.get_bottom(), store.get_top(), buff=0.1, color=INK)
        self.say("exp_engine_1", "In the eighteen thirties he designed something far bigger: the Analytical Engine. "
                                 "It was designed but never completed.")
        self.play(FadeIn(eng_title))
        self.say("exp_engine_2", "Punched cards gave it input. The Mill did the calculation, the Store held the "
                                 "numbers, and a printer produced the output.")
        self.play(FadeIn(cards_in), GrowArrow(a1), FadeIn(mill))
        self.play(GrowArrow(a3), FadeIn(store))
        self.play(GrowArrow(a2), FadeIn(printer))
        branch = T("+ could choose its next step from a result", 24, GOLD).next_to(store, DOWN, buff=0.3)
        self.say("exp_engine_3", "It could even choose its next step based on a result, just like a modern program.")
        self.play(FadeIn(branch))
        father = T("Charles Babbage — Father of the Computer", 30, GOLD, BOLD).move_to(DOWN * 3.3)
        self.say("exp_father", "This is why Charles Babbage is called the Father of the Computer.")
        self.play(FadeOut(branch), Write(father))
        self.wait_for_narration()
        self.play(FadeOut(VGroup(eng_title, cards_in, mill, printer, store, a1, a2, a3, father)))

        ada = card("Ada Lovelace", "1843", "method for Bernoulli numbers\n→ first computer programmer",
                   MECH, person_icon(GOLD), w=5.2).move_to(stage)
        self.say("exp_ada", "In eighteen forty-three, Ada Lovelace wrote a method for the Analytical Engine to "
                            "calculate Bernoulli numbers. For this she is known as the first computer programmer.")
        self.play(FadeIn(ada, shift=UP * 0.3))
        self.wait_for_narration()
        self.play(FadeOut(ada))

        # Electromechanical
        self.play(focus_band(bands, 2))
        holl = card("Tabulating Machine", "1890 · Herman Hollerith", "US census · punched cards\n→ later part of IBM",
                    ELMECH, relay_icon(ELMECH), w=4.6)
        mark = card("Harvard Mark I", "1944 · Howard Aiken", "electromechanical relays",
                    ELMECH, relay_icon(ELMECH), w=4.6)
        row = VGroup(holl, mark).arrange(RIGHT, buff=0.7).move_to(stage)
        self.say("exp_hollerith", "Next, electricity joins the gears. In eighteen ninety, Herman Hollerith's "
                                  "Tabulating Machine read punched cards to process the US census. "
                                  "His company later became part of IBM.")
        self.play(FadeIn(holl, shift=UP * 0.3))
        self.say("exp_mark1", "In nineteen forty-four, Howard Aiken's Harvard Mark One used electromechanical relays.")
        self.play(FadeIn(mark, shift=UP * 0.3))
        self.wait_for_narration()
        self.play(FadeOut(row))

        # Electronic
        self.play(focus_band(bands, 3))
        tubes = VGroup(*[tube_icon().scale(0.45) for _ in range(12)]).arrange_in_grid(rows=2, buff=0.25)
        eniac = VGroup(T("ENIAC · 1946 · Eckert & Mauchly", 30, ELEC, BOLD),
                       tubes,
                       T("~18,000 vacuum tubes · first general-purpose electronic digital computer", 22, INK))
        eniac.arrange(DOWN, buff=0.35).move_to(stage + UP * 0.3)
        fit(eniac, 12.5)
        self.say("exp_eniac", "Then came the electronic phase. In nineteen forty-six, Eckert and Mauchly built ENIAC, "
                              "with about eighteen thousand vacuum tubes. It was the first general-purpose "
                              "electronic digital computer.")
        self.play(FadeIn(eniac[0]), LaggedStart(*[FadeIn(t) for t in tubes], lag_ratio=0.05))
        self.play(FadeIn(eniac[2]))
        rewire = T("Reprogrammed by rewiring cables and switches — sometimes for days", 24, BAD)
        rewire.next_to(eniac, DOWN, buff=0.35)
        self.say("exp_rewire", "But to change its program, people had to rewire cables and switches, "
                               "sometimes for days.")
        self.play(FadeIn(rewire))
        self.wait_for_narration()
        self.play(FadeOut(VGroup(eniac, rewire)))

        mem = RoundedRectangle(corner_radius=0.15, width=3.6, height=2.4, stroke_color=ELEC, stroke_width=3)
        mem_lab = T("Memory", 24, ELEC, BOLD).next_to(mem.get_top(), DOWN, buff=0.2)
        slots = VGroup(*[VGroup(RoundedRectangle(corner_radius=0.08, width=2.8, height=0.6,
                                                 fill_color=col, fill_opacity=0.85, stroke_width=0),
                                T(t, 22, BG, BOLD))
                         for t, col in (("Instructions", GOLD), ("Data", GOOD))])
        for s in slots:
            s[1].move_to(s[0])
        slots.arrange(DOWN, buff=0.2).move_to(mem).shift(DOWN * 0.25)
        cpu = VGroup(RoundedRectangle(corner_radius=0.15, width=2.4, height=1.4,
                                      stroke_color=ELEC, stroke_width=3), T("CPU", 30, INK, BOLD))
        memory = VGroup(mem, mem_lab, slots)
        VGroup(memory, cpu).arrange(RIGHT, buff=2.0).move_to(stage + UP * 0.2)
        link = DoubleArrow(memory.get_right(), cpu.get_left(), buff=0.15, color=INK)
        sp_title = T("Stored-program concept · John von Neumann", 28, INK, BOLD).next_to(
            VGroup(memory, cpu), UP, buff=0.4)
        self.say("exp_stored", "The fix was the stored-program concept, described by John von Neumann. "
                               "Keep the instructions in memory, right next to the data, so the CPU can read both.")
        self.play(FadeIn(sp_title), Create(mem), FadeIn(mem_lab), FadeIn(cpu))
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.2) for s in slots], lag_ratio=0.4), GrowArrow(link))

        firsts = VGroup(
            T("EDSAC · 1949 · Cambridge — first practical stored-program computer", 24, INK),
            T("UNIVAC I · 1951 — first commercially produced computer in the US", 24, INK),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).to_edge(DOWN, buff=0.45)
        self.say("exp_edsac", "In nineteen forty-nine, EDSAC at Cambridge became the first practical "
                              "stored-program computer.")
        self.play(FadeIn(firsts[0], shift=UP * 0.2))
        self.say("exp_univac", "And in nineteen fifty-one, UNIVAC One became the first commercially produced "
                               "computer in the United States.")
        self.play(FadeIn(firsts[1], shift=UP * 0.2))
        self.end()

    # -- S04 -----------------------------------------------------------------

    def example(self):
        self.begin("S04_Example", "Example")

        title = T("Example 1 — Which machine is it?", 32, GOLD, BOLD).to_edge(UP, buff=0.9)
        clues = VGroup(*[T("•  " + c, 28, INK) for c in
                         ("Used gears", "Could add and subtract", "Could NOT multiply directly")])
        clues.arrange(DOWN, buff=0.3, aligned_edge=LEFT).shift(LEFT * 3 + UP * 0.6)
        self.say("ex1_1", "Example one. A machine used gears, could add and subtract, "
                          "but could not multiply directly. Which machine is it?")
        self.play(FadeIn(title))
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in clues], lag_ratio=0.5))
        self.wait_for_narration()

        step1 = T("Gears, no electricity  →  Mechanical phase", 26, MECH)
        cands = VGroup(card("Pascaline", "1642", "+  −  only", MECH, gear_icon(MECH), w=3.2, h=2.7),
                       card("Stepped Reckoner", "1673", "+  −  ×  ÷", MECH, twin_gears(MECH), w=3.2, h=2.7))
        cands.arrange(RIGHT, buff=0.5).shift(RIGHT * 3.2 + UP * 0.6)
        self.say("ex1_2", "Gears and no electricity puts it in the mechanical phase. "
                          "That leaves the Pascaline and the Stepped Reckoner.")
        self.play(FadeIn(cands))
        self.play(FadeIn(step1.next_to(cands, DOWN, buff=0.3)))
        answer = T("Answer: Pascaline", 30, GOOD, BOLD).next_to(step1, DOWN, buff=0.3)
        self.say("ex1_3", "The Stepped Reckoner could multiply, so it is out. The answer is the Pascaline.")
        self.play(cands[1].animate.set_opacity(0.3), Circumscribe(clues[1], color=GOLD))
        self.play(cands[0][0].animate.set_stroke(GOOD, width=6))
        self.play(Write(answer))
        self.wait_for_narration()
        self.play(FadeOut(VGroup(title, clues, cands, step1, answer)))

        title2 = T("Example 2 — Put them in order", 32, GOLD, BOLD).to_edge(UP, buff=0.9)
        bands = timeline().move_to(DOWN * 1.2)
        names = [("ENIAC", 3, 0.0), ("Napier's Bones", 0, 0.0), ("Analytical Engine", 1, 0.45),
                 ("Pascaline", 1, -0.45)]
        chips = VGroup()
        for name, _, _ in names:
            chip = VGroup(RoundedRectangle(corner_radius=0.12, width=2.9, height=0.7,
                                           fill_color=PANEL, fill_opacity=1, stroke_color=INK, stroke_width=2),
                          fit(T(name, 22, INK, BOLD), 2.6))
            chip[1].move_to(chip[0])
            chips.add(chip)
        chips.arrange(RIGHT, buff=0.3).move_to(UP * 1.4)
        self.say("ex2_1", "Example two. Put these in chronological order: ENIAC, Napier's Bones, "
                          "the Analytical Engine and the Pascaline.")
        self.play(FadeIn(title2), FadeIn(chips))
        self.play(FadeIn(bands))
        self.wait_for_narration()

        drop_lines = [
            "ENIAC used vacuum tubes, so it goes in the electronic phase.",
            "Napier's Bones were manual rods, the earliest phase.",
            "The Analytical Engine used gears, so it is mechanical.",
            "The Pascaline is also mechanical, and at sixteen forty-two it comes before Babbage's engine.",
        ]
        for i, (chip, (_, phase, dx), line) in enumerate(zip(chips, names, drop_lines)):
            target = bands[phase][0].get_top() + UP * 0.6 + RIGHT * dx * 3
            if phase == 1:
                target = bands[phase][0].get_top() + UP * (0.6 if dx < 0 else 1.45)
            self.say(f"ex2_drop_{i + 1}", line)
            self.play(chip.animate.scale(0.85).move_to(target).set_stroke(PHASES[phase][1]), run_time=0.9)
        self.wait_for_narration()

        order = T("Napier's Bones  →  Pascaline  →  Analytical Engine  →  ENIAC", 28, GOOD, BOLD)
        order.to_edge(DOWN, buff=0.6)
        tip = T("Place by phase first — use years only inside the same phase", 22, MUTED)
        tip.next_to(order, UP, buff=0.2)
        self.say("ex2_2", "So the order is Napier's Bones, Pascaline, Analytical Engine, ENIAC. "
                          "Place each machine by phase first, and use years only inside the same phase.")
        self.play(Write(order))
        self.play(FadeIn(tip))
        self.end()

    # -- S05 -----------------------------------------------------------------

    def exam_application(self):
        self.begin("S05_ExamApplication", "Exam Application")

        block = mcq("Which was the first mechanical calculator that could perform\n"
                    "all four basic arithmetic operations?",
                    [("A", "Pascaline"), ("B", "Stepped Reckoner"),
                     ("C", "Napier's Bones"), ("D", "Difference Engine")])
        block.move_to(DOWN * 0.1)
        q, rows = block
        self.say("exam_1", "Here is a typical exam question. Which was the first mechanical calculator that could "
                           "perform all four basic arithmetic operations?")
        self.play(FadeIn(q))
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rows], lag_ratio=0.2))
        self.wait_for_narration()

        # Text submobjects skip whitespace, so index into the text without spaces.
        glyphs = "".join(q.text.split())
        key = q[glyphs.find("allfour"):]
        key_box = SurroundingRectangle(key, color=GOLD, buff=0.06)
        self.say("exam_2", "The key words are all four operations.")
        self.play(Create(key_box), key.animate.set_color(GOLD))
        self.wait_for_narration()

        anim, _ = strike(rows[2])
        tag_c = tag_inside(rows[2], "manual rods")
        self.say("exam_c", "Napier's Bones are manual rods, not a mechanical calculator. Cross out C.")
        self.play(anim, FadeIn(tag_c))
        anim, _ = strike(rows[3])
        tag_d = tag_inside(rows[3], "tables, much later")
        self.say("exam_d", "The Difference Engine made tables, and came much later. Cross out D.")
        self.play(anim, FadeIn(tag_d))
        anim, _ = strike(rows[0])
        tag_a = tag_inside(rows[0], "+ − only")
        self.say("exam_a", "The Pascaline could only add and subtract. Cross out A.")
        self.play(anim, FadeIn(tag_a))
        self.say("exam_b", "That leaves B, the Stepped Reckoner.")
        self.play(mark_correct(rows[1]))
        self.wait_for_narration()

        trap = VGroup(RoundedRectangle(corner_radius=0.15, width=7.4, height=0.8,
                                       fill_color=BAD, fill_opacity=0.15, stroke_color=BAD, stroke_width=2),
                      T("Trap: the famous name (Pascaline) pulls you to A", 22, INK))
        trap[1].move_to(trap[0])
        trap.to_edge(DOWN, buff=0.3)
        self.say("exam_trap", "Watch out for the trap. The Pascaline is the more famous name, "
                              "and it pulls many students towards option A.")
        self.play(FadeIn(trap, shift=UP * 0.2), Indicate(rows[0], color=BAD, scale_factor=1.03))
        self.end()

    # -- S06 -----------------------------------------------------------------

    def common_mistakes(self):
        self.begin("S06_CommonMistake", "Common Mistakes")

        items = [
            ("“Famous” = “first”", "Match the exact capability the question asks for",
             "Mistake one: assuming the famous machine is the first one.",
             "Always match the exact capability the question asks for."),
            ("Babbage built the Analytical Engine", "He designed it — it was never completed",
             "Mistake two: saying Babbage built the Analytical Engine.",
             "He designed it, but it was never completed."),
            ("ENIAC stored its program in memory",
             "It was rewired; EDSAC was the first practical stored-program machine",
             "Mistake three: saying ENIAC stored its program in memory.",
             "ENIAC was rewired by hand. EDSAC was the first practical stored-program machine."),
        ]
        rows = VGroup()
        for wrong, right, _, _ in items:
            w = VGroup(T("✗", 34, BAD, BOLD), fit(T(wrong, 24, INK), 4.6)).arrange(RIGHT, buff=0.25)
            r = VGroup(T("✓", 34, GOOD, BOLD), fit(T(right, 22, INK), 6.2)).arrange(RIGHT, buff=0.25)
            box_w = RoundedRectangle(corner_radius=0.12, width=5.4, height=1.1, fill_color=BAD,
                                     fill_opacity=0.12, stroke_color=BAD, stroke_width=2)
            box_r = RoundedRectangle(corner_radius=0.12, width=7.0, height=1.1, fill_color=GOOD,
                                     fill_opacity=0.12, stroke_color=GOOD, stroke_width=2)
            w.move_to(box_w)
            r.move_to(box_r)
            rows.add(VGroup(VGroup(box_w, w), VGroup(box_r, r)).arrange(RIGHT, buff=0.35))
        rows.arrange(DOWN, buff=0.45).move_to(DOWN * 0.2)
        title = T("Three mistakes that cost marks", 32, GOLD, BOLD).to_edge(UP, buff=0.9)
        self.say("mistake_intro", "Here are three mistakes that cost students marks.")
        self.play(FadeIn(title))
        for i, (row, (_, _, say_wrong, say_right)) in enumerate(zip(rows, items)):
            self.say(f"mistake_{i + 1}_wrong", say_wrong)
            self.play(FadeIn(row[0], shift=RIGHT * 0.3))
            self.say(f"mistake_{i + 1}_right", say_right)
            self.play(FadeIn(row[1], shift=LEFT * 0.3))
        self.end()

    # -- S07 -----------------------------------------------------------------

    def practice_question(self):
        self.begin("S07_PracticeQuestion", "Practice Question")

        block = mcq("In Babbage's Analytical Engine, the “Mill” and the “Store”\n"
                    "correspond to which modern components?",
                    [("A", "Mill → Memory,  Store → CPU"),
                     ("B", "Mill → Processor (ALU),  Store → Memory"),
                     ("C", "Mill → Input unit,  Store → Output unit"),
                     ("D", "Mill → Memory,  Store → Output unit")])
        block.scale(0.92).move_to(DOWN * 0.3)
        q, rows = block
        pause = 6.0
        n = self.say("practice_1", "Your turn. In Babbage's Analytical Engine, the Mill and the Store correspond "
                                   "to which modern components? Pause and think.", pause_after=pause)
        self.play(FadeIn(q))
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.15) for r in rows], lag_ratio=0.2))
        self.wait_for_narration(n, include_pause=False)

        # Countdown ring during the thinking pause.
        tracker = ValueTracker(1.0)
        ring = always_redraw(lambda: Arc(radius=0.45, start_angle=PI / 2,
                                         angle=max(TAU * tracker.get_value(), 1e-3),
                                         stroke_color=GOLD, stroke_width=8).to_corner(DR, buff=0.5))
        think = T("Your turn", 22, GOLD, BOLD)
        self.add(ring)
        think.next_to(ring, LEFT, buff=0.3)
        self.play(FadeIn(think), run_time=0.3)
        self.play(tracker.animate.set_value(0.0), run_time=max(0.5, self.remaining(n) + pause - 0.3),
                  rate_func=linear)
        self.remove(ring)
        self.end()

    # -- S08 -----------------------------------------------------------------

    def answer_explanation(self):
        self.begin("S08_AnswerExplanation", "Answer and Explanation")

        ans = T("Answer: B", 40, GOOD, BOLD).to_edge(UP, buff=0.9)
        self.say("answer_1", "The answer is B.")
        self.play(Write(ans))

        pairs = [("Mill", "Processor (ALU)", MECH), ("Store", "Memory", ELMECH),
                 ("Punched cards", "Input", MANUAL), ("Printer", "Output", ELEC)]
        lines = [
            "The Mill is the processor, or ALU. Just as a mill grinds grain, the Mill grinds numbers.",
            "The Store is memory. A store keeps things until they are needed.",
            "The punched cards are the input,",
            "and the printer is the output.",
        ]
        left_head = T("Analytical Engine", 26, MUTED, BOLD)
        right_head = T("Modern computer", 26, MUTED, BOLD)
        rows = VGroup()
        for old, new, col in pairs:
            l = VGroup(RoundedRectangle(corner_radius=0.12, width=3.6, height=0.8, stroke_color=col,
                                        stroke_width=3, fill_color=PANEL, fill_opacity=1), T(old, 26, INK, BOLD))
            r = VGroup(RoundedRectangle(corner_radius=0.12, width=3.6, height=0.8, stroke_color=col,
                                        stroke_width=3, fill_color=col, fill_opacity=0.2), T(new, 26, INK, BOLD))
            l[1].move_to(l[0])
            r[1].move_to(r[0])
            rows.add(VGroup(l, r).arrange(RIGHT, buff=2.2))
        rows.arrange(DOWN, buff=0.3).move_to(DOWN * 0.5)
        left_head.next_to(rows[0][0], UP, buff=0.3)
        right_head.next_to(rows[0][1], UP, buff=0.3)
        self.play(FadeIn(left_head), FadeIn(right_head))

        grind = T("a mill grinds grain → the Mill “grinds” numbers", 22, GOLD).to_edge(DOWN, buff=0.4)
        keep = T("a store keeps things until needed → memory", 22, GOLD).to_edge(DOWN, buff=0.4)
        for i, (row, line) in enumerate(zip(rows, lines)):
            self.say(f"answer_pair_{i + 1}", line)
            arrow = DoubleArrow(row[0].get_right(), row[1].get_left(), buff=0.15, color=INK)
            self.play(FadeIn(row[0]), GrowArrow(arrow), FadeIn(row[1]))
            if i == 0:
                self.play(FadeIn(grind))
            if i == 1:
                self.play(ReplacementTransform(grind, keep))
        close = T("Same basic units as a computer today", 26, GOOD, BOLD).to_edge(DOWN, buff=0.4)
        self.say("answer_2", "These are the same basic units found in a computer today.")
        self.play(ReplacementTransform(keep, close))
        self.end()

    # -- S09 -----------------------------------------------------------------

    def quick_revision(self):
        self.begin("S09_QuickRevision", "Quick Revision")

        bands = timeline().to_edge(UP, buff=0.9)
        self.say("rev_intro", "Let's revise quickly.")
        self.play(FadeIn(bands))
        notes = [
            ["Abacus", "Napier's Bones (1617)", "human does the thinking"],
            ["Pascaline: + −", "Stepped Reckoner: + − × ÷", "Jacquard: punched cards",
             "Babbage: Analytical Engine", "Lovelace: first programmer"],
            ["Hollerith tabulator (1890)", "Harvard Mark I (1944)"],
            ["ENIAC (1946): first general-", "purpose electronic digital", "EDSAC (1949): stored program",
             "UNIVAC I (1951): commercial"],
        ]
        lines = [
            "Manual: the abacus and Napier's Bones, where the human does the thinking.",
            "Mechanical: the Pascaline adds and subtracts, the Stepped Reckoner does all four operations, "
            "Jacquard brings punched cards, Babbage designs the Analytical Engine, and Ada Lovelace "
            "becomes the first programmer.",
            "Electromechanical: Hollerith's tabulator and the Harvard Mark One.",
            "Electronic: ENIAC, the first general-purpose electronic digital computer, EDSAC with its "
            "stored program, and UNIVAC One, the first commercial computer.",
        ]
        for i, (items, line) in enumerate(zip(notes, lines)):
            col = PHASES[i][1]
            stack = VGroup(*[fit(T(l, 19, INK), 3.0) for l in items]).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
            panel = RoundedRectangle(corner_radius=0.12, width=3.15, height=4.6, stroke_color=col,
                                     stroke_width=2, fill_color=PANEL, fill_opacity=1)
            panel.next_to(bands[i], DOWN, buff=0.25)
            stack.move_to(panel).align_to(panel, UP).shift(DOWN * 0.3)
            self.say(f"rev_phase_{i + 1}", line)
            self.play(focus_band(bands, i), FadeIn(panel), run_time=0.6)
            self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in stack], lag_ratio=0.3))
        self.end()

    # -- S10 -----------------------------------------------------------------

    def closing(self):
        self.begin("S10_Closing", "Closing")

        start = VGroup(abacus_icon().scale(0.6), T("beads on a rod", 22, MUTED)).arrange(DOWN, buff=0.2)
        end = VGroup(mainframe_icon(ELEC).scale(0.8), T("program held in memory", 22, MUTED)).arrange(DOWN, buff=0.2)
        VGroup(start, end).arrange(RIGHT, buff=5).move_to(UP * 1.2)
        path = Arrow(start.get_right(), end.get_left(), buff=0.3, color=GOLD, stroke_width=6)
        self.say("close_1", "We travelled from beads on a rod to a machine that holds its own program in memory.")
        self.play(FadeIn(start), GrowArrow(path), FadeIn(end))
        self.wait_for_narration()

        steps = ["Vacuum tubes", "Transistors", "Integrated circuits", "Microprocessors"]
        chain = VGroup()
        for i, s in enumerate(steps):
            chip = VGroup(RoundedRectangle(corner_radius=0.15, width=2.8, height=0.8, stroke_color=ELEC,
                                           stroke_width=3, fill_color=ELEC, fill_opacity=0.12 + 0.18 * i),
                          fit(T(s, 22, INK, BOLD), 2.5))
            chip[1].move_to(chip[0])
            chain.add(chip)
        chain.arrange(RIGHT, buff=0.55).move_to(DOWN * 1.0)
        arrows = VGroup(*[Arrow(chain[i].get_right(), chain[i + 1].get_left(), buff=0.05,
                                color=INK, stroke_width=4, max_tip_length_to_length_ratio=0.35)
                          for i in range(3)])
        self.say("close_2", "From here, vacuum tubes gave way to transistors, then integrated circuits, "
                            "and then microprocessors.")
        for i, c in enumerate(chain):
            self.play(FadeIn(c, shift=RIGHT * 0.2), *([GrowArrow(arrows[i - 1])] if i else []), run_time=0.8)
            self.wait(0.8)
        self.wait_for_narration()

        nxt = VGroup(T("Next:", 28, MUTED), T("Generations of Computers", 36, GOLD, BOLD)).arrange(RIGHT, buff=0.3)
        nxt.to_edge(DOWN, buff=0.6)
        self.say("close_3", "That is exactly where our next lesson begins: the Generations of Computers. See you there.")
        self.play(Write(nxt))
        self.end()
