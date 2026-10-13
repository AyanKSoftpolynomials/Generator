"""
animation.py for the LMS video generator.

Topic  : Array - Actual Classroom Teaching Script (conversational story mode)

Source script:
  Array_Actual_Classroom_Teaching_Script.docx
  Two speakers, kept as separate blocks:
    - TEACHER blocks: ``self.teacher(...)`` (TEACHER_VOICE). They drive the board.
    - STUDENT blocks: ``self.student(...)`` (STUDENT_VOICE). Every student answer
      is its own narration and appears as a "Student" card at the bottom right.
  Consecutive lines by the same speaker share one block. Stage directions
  ("The board now shows ...") are not narrated; they become the visuals.
  Every question is on screen.
  Facts checked: marks = [72, 85, 64, 91, 78] -> marks[1] = 85;
  ages = [21, 24, 22, 25, 23] -> ages[3] = 25, ages[0] = 21, valid indexes 0-4,
  ages[5] does not exist (last index = 5 - 1 = 4).

Style: 2D only, three colours (blue main, grey support, gold highlight), one
``LMSScene`` class, narration as the timeline, ``fitted_text`` for all text.
Pinned ARRAY IDEAS panel from "One name, many values" to the end.

Section map:
  S00 Recap: a variable   S01 Too many variables   S02 One name, many values
  S03 The index   S04 Why zero?   S05 Let's test it   S06 Why arrays matter
  S07 In our own words   S08 Next: array to memory
"""

import math
import re

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#0B1020"
INK = "#E6EAF2"
MUTED = "#8B95A7"
PANEL = "#151C2E"
CELL = "#1B2440"
FOCUS = "#FFD54F"      # "look here" / prediction / main idea
GOOD = "#66BB6A"       # correct / confirmed
BAD = "#EF5350"        # trap / eliminated
TURN = "#FF8A65"       # turn words ("However", "But", "Yet")
HINT = "#4FC3F7"       # locating / the passage's evidence
ACCENT = "#BA68C8"     # secondary accent
SOFT = "#F48FB1"       # tertiary accent

# Three-colour palette for the whole video: blue (main), grey (support), gold (highlight).
MAIN = "#4FC3F7"
GOLD = "#FFD54F"
HINT = GOOD = ACCENT = SOFT = MAIN
FOCUS = BAD = TURN = GOLD

FONT = "Segoe UI"
MIN_FONT = 22          # readable floor: text is never shrunk below this
TITLE = 46
BODY = 30
LABEL = 28
SMALL = 24

# ============================================================= layout ====

FRAME_W = config.frame_width
FRAME_H = config.frame_height
SAFE = 0.45                                   # margin kept clear on every side
SAFE_W = FRAME_W - 2 * SAFE

CARD_TOP = FRAME_H / 2 - SAFE - 0.2           # top edge of a heading card
FLOOR_Y = -FRAME_H / 2 + SAFE + 0.15          # lowest y any content may reach
DEPTH_DIR = np.array([0.5, 0.32, 0.0])        # screen direction of "into the page"

# Pinned reference panel (left) and the stage it leaves free (right).
PANEL_W = 3.6
PANEL_X = -FRAME_W / 2 + SAFE + PANEL_W / 2
PANEL_Y = 0.5
STAGE_LEFT = PANEL_X + PANEL_W / 2 + 0.4
STAGE_RIGHT = FRAME_W / 2 - SAFE
STAGE_W = STAGE_RIGHT - STAGE_LEFT
STAGE_X = (STAGE_LEFT + STAGE_RIGHT) / 2

STEPS = ["READ", "PREDICT", "ELIMINATE", "CONFIRM"]


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, disable_ligatures=True)


def fit_width(mob, max_width):
    """Scale ``mob`` down (never up) to at most ``max_width``."""
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    return mob


def wrap_words(s, max_chars):
    """Greedy word wrap into lines of at most ``max_chars`` characters."""
    lines, line = [], ""
    for word in s.split():
        if line and len(line) + 1 + len(word) > max_chars:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    lines.append(line)
    return "\n".join(lines)


def wrap_lines(s, n_lines):
    """Wrap ``s`` into at most ``n_lines`` lines that are as even as possible."""
    for max_chars in range(math.ceil(len(s) / n_lines), len(s) + 1):
        wrapped = wrap_words(s, max_chars)
        if wrapped.count("\n") < n_lines:
            return wrapped
    return s


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3):
    """Readable text no wider than ``max_width``.

    Order of preference: as written > slightly smaller (to 85 %) > wrapped
    over more lines > wrapped and smaller (never below MIN_FONT). If none of
    that fits, fail loudly.
    """
    floor = max(MIN_FONT, 0.85 * size)
    for lines in range(1, max_lines + 1):
        body = s if lines == 1 else wrap_lines(s, lines)
        mob = text(body, size, color, weight)
        if mob.width <= max_width:
            return mob
        if size * max_width / mob.width >= floor:
            return mob.scale(max_width / mob.width)
        floor = MIN_FONT
    if size * max_width / mob.width >= MIN_FONT:
        return mob.scale(max_width / mob.width)
    raise ValueError(f"Text {s!r} cannot fit {max_width:.2f} units at a readable size; "
                     "shorten it or give it a wider container.")


def pill(label, color=FOCUS, size=SMALL, fill_opacity=0.14):
    """Short keyword tag. The box is sized from the text, so text cannot escape."""
    t = text(label, size, color, BOLD)
    box = RoundedRectangle(corner_radius=(t.height + 0.26) / 2, width=t.width + 0.5, height=t.height + 0.26,
                           stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=fill_opacity)
    t.move_to(box)
    return VGroup(box, t)


def tick_row(s, width, color=GOOD, mark="✓", size=BODY, max_lines=3):
    """A checklist row: mark + fitted text."""
    return VGroup(text(mark, size + 4, color, BOLD),
                  fitted_text(s, width, size, INK, max_lines=max_lines)).arrange(RIGHT, buff=0.3)


# ================================================== 3D-look helpers ====

def tint(color, amount, towards=BLACK):
    """``color`` moved ``amount`` of the way towards ``towards``."""
    return interpolate_color(ManimColor(color), ManimColor(towards), amount)


class Slab(VGroup):
    """A box drawn with depth: front face, lit top, shaded right side and a
    soft shadow. Labels go on ``front`` so text stays flat and readable."""

    def __init__(self, width, height, color, depth=0.28, fill=PANEL):
        super().__init__()
        d = DEPTH_DIR * depth
        self.front = Rectangle(width=width, height=height, stroke_color=color, stroke_width=2.5,
                               fill_color=fill, fill_opacity=1)
        ul, ur, dr = self.front.get_corner(UL), self.front.get_corner(UR), self.front.get_corner(DR)
        self.top = Polygon(ul, ur, ur + d, ul + d, stroke_color=color, stroke_width=2,
                           fill_color=tint(color, 0.55), fill_opacity=1)
        self.side = Polygon(ur, dr, dr + d, ur + d, stroke_color=color, stroke_width=2,
                            fill_color=tint(color, 0.75), fill_opacity=1)
        self.shadow = Ellipse(width=width + depth * 1.6, height=0.14 + depth * 0.5, stroke_width=0,
                              fill_color=BLACK, fill_opacity=0.45)
        self.shadow.move_to(self.front.get_bottom() + d * 0.5 + DOWN * 0.06)
        self.add(self.shadow, self.side, self.top, self.front)


# ===================================================== this video ====

CRUMB_SUBJECT = "Programming"
CRUMB_MODULE = "Arrays"
CRUMB_TOPIC = "What Is an Array"
LESSON_TAG = "Arrays"
VIDEO_COUNT = 1

TEACHER_VOICE = "default"
STUDENT_VOICE = "default"      # set to your student voice id to give students a different voice
TEACHER_PAUSE = 0.7            # silence after each teacher block (seconds), so speakers never run together
STUDENT_PAUSE = 0.6            # silence after each student block

IDEAS = [("One name, many values", GOLD), ("Each value is an element", MAIN), ("Index starts at 0", MAIN),
         ("Last index = count − 1", MAIN)]
P_NAME, P_ELEM, P_INDEX, P_LAST = range(4)

MARKS = [72, 85, 64, 91, 78]
AGES = [21, 24, 22, 25, 23]
CELL = 0.95
ROW_X = 3.0          # array rows sit right of centre so the name label fits on the left


def array_row(values, color=MAIN):
    """An array as a row of raised boxes (drawn depth), one value on each front face.

    Each cell is VGroup(slab, value); ``cell[0].front`` is the front face."""
    cells = VGroup()
    for k, v in enumerate(values):
        slab = Slab(CELL, CELL, color, depth=0.18)
        cells.add(VGroup(slab, text(str(v), BODY, INK, BOLD).move_to(slab.front)).shift(RIGHT * k * CELL))
    return cells


def index_labels(cells):
    """Gold index numbers above each cell."""
    return VGroup(*[text(str(k), LABEL, GOLD, BOLD).next_to(c, UP, buff=0.22) for k, c in enumerate(cells)])


class ArrayClassroomVideo(LMSScene):
    lesson_title = "Array"

    def construct(self):
        self.camera.background_color = BG
        self.pinned = []
        self.panel = None
        self.bubble = None

        self.recap()
        self.too_many()
        self.one_name()
        self.the_index()
        self.why_zero()
        self.test_it()
        self.why_arrays()
        self.own_words()
        self.next_session()

    # ---------------------------------------------------- scene helpers --

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything except pinned mobjects."""
        keep = set()
        for p in self.pinned:
            keep.update(p.get_family())
        others = [m for m in self.mobjects if m not in keep]
        if others:
            self.play(FadeOut(Group(*others)), run_time=run_time)

    def card(self, content, width=None, height=None, color=MUTED, pad=0.3):
        """Container-aware card (grows to content, or fits content to a fixed width)."""
        if width is not None:
            fit_width(content, width - 2 * pad)
        w = width if width is not None else content.width + 2 * pad
        h = max(height or 0, content.height + 2 * pad)
        box = RoundedRectangle(corner_radius=0.18, width=w, height=h, stroke_color=color,
                               stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
        box.move_to(content)
        self.validator.check_fit(content, box, margin=0.1)
        return VGroup(box, content)

    def stage(self):
        """(centre x, width) of the free area: full frame, or right of the pinned panel."""
        if self.panel is not None and self.panel in self.pinned:
            return STAGE_X, STAGE_W
        return 0.0, SAFE_W

    def heading(self, s, color=FOCUS):
        """A heading card under the top edge of the free area."""
        x, w = self.stage()
        t = fitted_text(s, w - 1.0, BODY, INK, BOLD, max_lines=2)
        c = self.card(t, color=color)
        return c.move_to(RIGHT * x + UP * (CARD_TOP - c.height / 2))

    # ------------------------------------------------ pinned side panel --

    def undock(self):
        """Release the panel (before the recap)."""
        self.pinned.clear()
        self.play(FadeOut(self.panel), run_time=0.6)
        self.panel = None

    def light(self, *ks):
        """Light panel rows ``ks``; dim the others."""
        anims = []
        for i, row in enumerate(self.panel.rows):
            if i in ks:
                row.label.set_color(row.color)
                anims.append(Indicate(row, color=row.color, scale_factor=1.12))
            else:
                anims.append(row.label.animate.set_color(MUTED))
        return AnimationGroup(*anims)

    def all_lit(self):
        return AnimationGroup(*[row.label.animate.set_color(row.color) for row in self.panel.rows])

    # ------------------------------------------------- content builders --

    # ------------------------------------------------- shared scenes --

    # ---------------------------------------------- pinned panel (compact) --

    def compact_panel(self, title, items, color=MUTED):
        """A docked checklist on the left with one-line rows (fits up to seven rows)."""
        rows = VGroup()
        for name, c in items:
            chip = Square(0.22, stroke_width=0, fill_color=c, fill_opacity=0.9)
            label = self.card_text(name, PANEL_W - 1.1, c, BOLD)
            row = VGroup(chip, label).arrange(RIGHT, buff=0.22)
            row.label, row.color = label, c
            rows.add(row)
        rows.arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        content = VGroup(text(title, SMALL, MUTED, BOLD), rows).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        panel = self.card(content, width=PANEL_W, color=color)
        panel.move_to(RIGHT * PANEL_X + UP * (CARD_TOP - panel.height / 2))
        panel.rows = rows
        return panel

    def open_panel(self, title, items, color=FOCUS):
        """Dock the empty panel frame and pin it; rows are added later with ``add_row``."""
        self.panel = self.compact_panel(title, items, color)
        self.play(FadeIn(self.panel[0]), FadeIn(self.panel[1][0]), run_time=0.8)
        self.pinned.append(self.panel)
        self.validator.check_in_frame(self.panel)

    def add_row(self, k, source=None):
        """Panel row ``k`` grows out of ``source`` (or slides in)."""
        row = self.panel.rows[k]
        if source is None:
            self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.6)
        else:
            self.play(TransformFromCopy(source, row), run_time=0.9)

    # ------------------------------------------------------ cloze passage --

    # ------------------------------------------------------ shared scenes --

    # ------------------------------------------------------- maths helpers --

    @staticmethod
    def flex_text(s, width, color, weight=NORMAL):
        """Body text that steps down in size and up in lines rather than failing."""
        for sz, lines in [(BODY, 2), (BODY, 3), (LABEL, 3), (SMALL, 4), (MIN_FONT, 5)]:
            try:
                return fitted_text(s, width, sz, color, weight, max_lines=lines)
            except ValueError:
                continue
        return fitted_text(s, width, MIN_FONT, color, NORMAL, max_lines=8)

    @staticmethod
    def card_text(s, width, color, weight=NORMAL):
        """Text for a narrow card: 26 pt if it fits in four lines, else 24 pt in up to five."""
        for sz, wt, lines in [(SMALL + 2, weight, 4), (SMALL, weight, 5), (MIN_FONT, NORMAL, 6)]:
            try:
                return fitted_text(s, width, sz, color, wt, max_lines=lines)
            except ValueError:
                continue
        return fitted_text(s, width, MIN_FONT, color, NORMAL, max_lines=8)

    def question_box(self, s, color=FOCUS, label="Question"):
        """The full question, on screen as a card: a small label over the wording."""
        x, w = self.stage()
        body = VGroup(text(label, SMALL, color, BOLD), self.flex_text(s, w - 0.8, INK)).arrange(DOWN, buff=0.12,
                                                                                               aligned_edge=LEFT)
        return self.card(body, width=w - 0.2, color=color)

    # ---------------------------------------------- standard maths scenes --

    # ---------------------------------------------- odd-man-out helpers --

    # ------------------------------------------------------ speaker blocks --

    def teacher(self, nid, s):
        """A teacher block: the student card (if any) leaves, then the teacher speaks."""
        self.hush()
        return self.narrate(id=nid, text=s, voice=TEACHER_VOICE, subtitle=True, pause_after=TEACHER_PAUSE)

    def student(self, nid, spoken, shown=None, who="Student"):
        """A student block: the answer appears as a card, then the student speaks it."""
        self.say(shown or spoken, who)
        return self.narrate(id=nid, text=spoken, voice=STUDENT_VOICE, subtitle=True, pause_after=STUDENT_PAUSE)

    def say(self, s, who="Student"):
        """The student card at the bottom right (replaces the previous one)."""
        x, w = self.stage()
        body = VGroup(text(who, SMALL, MUTED, BOLD), fitted_text(s, 3.6, LABEL, INK, max_lines=3))
        body.arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        card = self.card(body, color=MUTED, pad=0.2)
        card.move_to(RIGHT * (x + w / 2 - card.width / 2 - 0.05) + UP * (FLOOR_Y + card.height / 2 + 0.05))
        self.validator.check_in_frame(card)
        anims = [FadeIn(card, shift=UP * 0.15)]
        if self.bubble is not None:
            anims.append(FadeOut(self.bubble))
        self.bubble = card
        self.play(*anims, run_time=0.4)

    def hush(self):
        """Remove the student card, if any."""
        if self.bubble is not None:
            self.play(FadeOut(self.bubble), run_time=0.3)
            self.bubble = None

    def wipe(self):
        self.clear_stage()
        self.bubble = None

    # ------------------------------------------------------ board helpers --

    def note(self, s, y, color=MAIN):
        """A note pill in the left column of the free area (clear of the student card)."""
        x, w = self.stage()
        p = pill(s, color, LABEL)
        fit_width(p, 4.6)
        return p.move_to(RIGHT * (x - w / 2 + p.width / 2 + 0.1) + UP * y)

    def named_row(self, name, values, y):
        """Array cells at ``ROW_X`` with the array's name on the left."""
        cells = array_row(values).move_to(RIGHT * ROW_X + UP * y)
        label = text(name, BODY, MAIN, BOLD).next_to(cells, LEFT, buff=0.3)
        return cells, label

    def mark_cell(self, cell, color=GOLD):
        return cell[0].front.animate.set_stroke(color, 4).set_fill(tint(color, 0.6), 1)

    # ============================================== 0. RECAP ============

    def recap(self):
        self.scene_start("S00_recap", title="Recap: a Variable")

        heading = self.heading("Arrays", GOLD)
        reminder = self.card(text("Last session: a variable gives a name to a value", LABEL, INK), color=MUTED)
        reminder.next_to(heading, DOWN, buff=0.5)
        box = VGroup(text("marks1", BODY, MAIN, BOLD), Arrow(LEFT * 0.6, RIGHT * 0.6, color=MUTED, stroke_width=4),
                     array_row([72])).arrange(RIGHT, buff=0.3).next_to(reminder, DOWN, buff=0.6)
        many = pill("but a lot of related values?", GOLD, BODY).next_to(box, DOWN, buff=0.6)
        self.validator.check_in_frame(VGroup(heading, reminder, box, many))

        self.play(FadeIn(heading, shift=DOWN * 0.3), FadeIn(reminder))
        n = self.teacher("recap_01", "Last time, we learned that a variable gives us a name for a value. But what happens "
                                     "when we have a lot of related values?")
        self.at_word(n, "name")
        self.play(FadeIn(box, shift=RIGHT * 0.2))
        self.at_word(n, "lot")
        self.play(FadeIn(many, scale=1.1))
        self.wait_for_narration(n)

        self.wipe()
        self.scene_end("S00_recap")

    # ===================================== 1. TOO MANY VARIABLES =========

    def too_many(self):
        self.scene_start("S01_too_many", title="Too Many Variables")

        heading = self.heading("Storing the marks of many students", MAIN)
        q1 = self.question_box("We want to store the marks of five students. How would we do that?")
        q1.next_to(heading, DOWN, buff=0.3)
        q_look = self.question_box("What might those variables look like?")
        q_look.move_to(q1)
        boxes = VGroup(*[self.card(text(f"marks{k}", LABEL, MAIN, BOLD), width=1.7, color=MAIN, pad=0.18)
                         for k in range(1, 6)]).arrange(RIGHT, buff=0.2).move_to(UP * 0.3)

        def grid(n_, rows, cols, side):
            g = VGroup(*[Square(side, stroke_width=1, stroke_color=MAIN, fill_color=MAIN, fill_opacity=0.5)
                         for _ in range(n_)])
            return g.arrange_in_grid(rows, cols, buff=side * 0.3).move_to(RIGHT * 1.2 + DOWN * 1.2)

        g50 = grid(50, 5, 10, 0.26)
        g500 = grid(500, 20, 25, 0.08)
        counts = [pill(s, GOLD, BODY).move_to(LEFT * 4.6 + DOWN * 0.9)
                  for s in ("5 variables", "50 variables", "500 variables", "5,000 ?!")]
        q2 = self.question_box("Fifty students? Still manageable? Five hundred? Five thousand?")
        q2.move_to(q1)
        q3 = self.question_box("Can we keep all those related values together under one name?")
        q3.move_to(q1)
        sep = pill("related values, each treated as a separate variable", MUTED, LABEL)
        fit_width(sep, 6.0).move_to(LEFT * 3.4 + DOWN * 2.7)
        self.validator.check_in_frame(VGroup(heading, q1, boxes, g500, sep, *counts))

        self.play(FadeIn(heading, shift=DOWN * 0.3))
        n = self.teacher("many_01", "Suppose we want to store the marks of five students. How would we do that?")
        self.at_word(n, "store")
        self.play(FadeIn(q1, shift=UP * 0.15))
        self.wait_for_narration(n)

        n = self.student("many_02", "Five variables.")
        self.wait_for_narration(n)

        n = self.teacher("many_03", "Alright. What might those variables look like?")
        self.at_word(n, "look")
        self.play(ReplacementTransform(q1, q_look))
        self.wait_for_narration(n)

        n = self.student("many_04", "marks one, marks two, marks three, marks four, marks five.",
                         "marks1, marks2, marks3, marks4, marks5.")
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.15) for b in boxes], lag_ratio=0.3), run_time=2.0)
        self.wait_for_narration(n)

        n = self.teacher("many_05", "Perfect. That works for five students. Now imagine we have fifty.")
        self.at_word(n, "Perfect")
        self.play(FadeIn(counts[0], scale=1.1))
        self.at_word(n, "fifty")
        self.play(ReplacementTransform(q_look, q2), FadeOut(boxes), FadeIn(g50),
                  ReplacementTransform(counts[0], counts[1]))
        self.wait_for_narration(n)

        n = self.teacher("many_06", "Still manageable? What about five hundred?")
        self.at_word(n, "hundred")
        self.play(ReplacementTransform(g50, g500), ReplacementTransform(counts[1], counts[2]))
        self.wait_for_narration(n)

        n = self.student("many_07", "Five hundred variables?", who="A student, laughing")
        self.wait_for_narration(n)

        n = self.teacher("many_08", "And what if our college has five thousand students?")
        self.at_word(n, "thousand")
        self.play(ReplacementTransform(counts[2], counts[3]))
        self.play(Indicate(counts[3], color=GOLD))
        self.wait_for_narration(n)

        n = self.student("many_09", "Okay, that definitely doesn't sound practical.",
                         "Okay… that definitely doesn't sound practical.")
        self.wait_for_narration(n)

        n = self.teacher("many_10", "Exactly. We have a collection of related values, but we are treating every value as "
                                    "a completely separate variable. So here's the real question: can we keep all those "
                                    "related values together under one name?")
        self.at_word(n, "collection")
        self.play(FadeIn(sep, shift=UP * 0.1))
        self.at_word(n, "together")
        self.play(ReplacementTransform(q2, q3))
        self.play(Circumscribe(q3, color=GOLD))
        self.wait_for_narration(n)

        self.wipe()
        self.scene_end("S01_too_many")

    # ===================================== 2. ONE NAME, MANY VALUES ======

    def one_name(self):
        self.scene_start("S02_one_name", title="One Name, Many Values")
        self.open_panel("Array ideas", IDEAS)

        heading = self.heading("The idea behind an array", GOLD)
        code = self.card(text("marks = [72, 85, 64, 91, 78]", BODY, MAIN, BOLD), color=MAIN)
        code.next_to(heading, DOWN, buff=0.35).set_x(STAGE_X)
        cells, label = self.named_row("marks", MARKS, 0.1)
        whole = SurroundingRectangle(VGroup(label, cells), color=GOLD, buff=0.15)
        elem = pill("element", GOLD, LABEL).move_to(RIGHT * 1.4 + DOWN * 1.4)
        self.validator.check_in_frame(VGroup(heading, code, cells, label, whole, elem))

        n = self.student("one_01", "Something like one variable containing many values?", who="A student, hand raised")
        self.wait_for_narration(n)

        n = self.teacher("one_02", "Exactly. And that is the idea behind an array.")
        self.at_word(n, "array")
        self.play(FadeIn(heading, shift=DOWN * 0.3))
        self.wait_for_narration(n)

        n = self.teacher("one_03", "Look at this. We have one name, marks, but several values inside it.")
        self.at_word(n, "Look")
        self.play(FadeIn(code, shift=UP * 0.15))
        self.at_word(n, "name")
        self.play(FadeIn(label), TransformFromCopy(code, cells), run_time=1.0)
        self.add_row(P_NAME, label)
        self.wait_for_narration(n)

        n = self.student("one_04", "So marks represents the whole collection?")
        self.play(Create(whole))
        self.wait_for_narration(n)

        n = self.teacher("one_05", "Yes. Each individual value inside that collection is called an element.")
        self.at_word(n, "element")
        self.play(FadeOut(whole), *[c.animate.shift(RIGHT * 0.25 * k) for k, c in enumerate(cells)])
        arrow = Arrow(elem.get_top(), cells[1].get_bottom(), color=GOLD, buff=0.1, stroke_width=4)
        self.play(FadeIn(elem), GrowArrow(arrow))
        self.add_row(P_ELEM, elem)
        self.wait_for_narration(n)

        self.wipe()
        self.scene_end("S02_one_name")

    # ============================================== 3. THE INDEX =========

    def the_index(self):
        self.scene_start("S03_index", title="The Index")

        heading = self.heading("Which value? The index", MAIN)
        q1 = self.question_box("I only want the mark 85. How do I tell the computer which value I want?")
        q1.next_to(heading, DOWN, buff=0.3).set_x(STAGE_X)
        cells, label = self.named_row("marks", MARKS, -0.9)
        idx = index_labels(cells)
        tag = text("index", LABEL, GOLD, BOLD).next_to(idx, LEFT, buff=0.3).align_to(label, RIGHT)
        q2 = self.question_box("So 85 is at which index?")
        q2.move_to(q1)
        ans = self.note("marks[1] = 85", -2.2, GOLD)
        self.validator.check_in_frame(VGroup(heading, q1, cells, label, idx, tag, ans))

        self.play(FadeIn(heading, shift=DOWN * 0.3), FadeIn(label), FadeIn(cells))
        n = self.teacher("index_01", "Now suppose I only want the mark eighty-five. How do I tell the computer which value "
                                     "I want?")
        self.at_word(n, "suppose")
        self.play(FadeIn(q1, shift=UP * 0.15))
        self.at_word(n, "eighty-five")
        self.play(self.mark_cell(cells[1]))
        self.wait_for_narration(n)

        n = self.student("index_02", "The second value?")
        self.wait_for_narration(n)

        n = self.teacher("index_03", "Right. But the computer needs a precise way to identify its position. That's where "
                                     "the index comes in.")
        self.at_word(n, "index")
        self.play(FadeIn(tag), LaggedStart(*[FadeIn(i_, shift=DOWN * 0.15) for i_ in idx], lag_ratio=0.15))
        self.wait_for_narration(n)

        n = self.teacher("index_04", "So eighty-five is at which index?")
        self.at_word(n, "which")
        self.play(ReplacementTransform(q1, q2))
        self.wait_for_narration(n)

        n = self.student("index_05", "Index one.", "Index 1.")
        self.play(Indicate(idx[1], color=GOLD, scale_factor=1.4))
        self.wait_for_narration(n)

        n = self.teacher("index_06", "Correct.")
        self.at_word(n, "Correct")
        self.play(FadeIn(ans, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.wipe()
        self.scene_end("S03_index")

    # ============================================== 4. WHY ZERO? ========

    def why_zero(self):
        self.scene_start("S04_zero", title="Why Zero?")

        heading = self.heading("Why does indexing start at 0?", MAIN)
        cells, label = self.named_row("marks", MARKS, 0.7)
        idx = index_labels(cells)
        start0 = self.note("indexing starts at 0", -1.5, GOLD)
        ptr = Arrow(cells[0].get_bottom() + DOWN * 0.75, cells[0].get_bottom() + DOWN * 0.05, color=GOLD, buff=0,
                    stroke_width=5)
        moves = [text(s, SMALL, GOLD, BOLD).next_to(cells[k], DOWN, buff=0.85)
                 for k, s in enumerate(["0 moves", "1 move", "2 moves", "3 moves", "4 moves"])]
        chain = self.note("0 → 1 → 2 → 3 → 4", -2.6)
        point = self.note("position 0, not value 0", -2.6, GOLD)
        self.validator.check_in_frame(VGroup(heading, cells, label, idx, start0, ptr, *moves, chain))

        self.play(FadeIn(heading, shift=DOWN * 0.3), FadeIn(label), FadeIn(cells), FadeIn(idx))
        n = self.student("zero_01", "Why is it one? It's the second value.", "Why is it 1? It's the second value.",
                         who="A student, confused")
        self.play(Indicate(idx[1], color=GOLD, scale_factor=1.4))
        self.wait_for_narration(n)

        n = self.teacher("zero_02", "That is because programming usually starts indexing at zero.")
        self.at_word(n, "programming")
        self.play(FadeIn(start0, shift=UP * 0.1))
        self.add_row(P_INDEX, start0)
        self.wait_for_narration(n)

        n = self.student("zero_03", "Why zero?")
        self.wait_for_narration(n)

        n = self.teacher("zero_04", "Think of it as how far you have moved from the beginning. Zero moves gives the first "
                                    "element. The next element is one position away, then two, three, and so on.")
        self.at_word(n, "far")
        self.play(GrowArrow(ptr), FadeIn(moves[0]))
        self.at_word(n, "Zero")
        self.play(self.mark_cell(cells[0]))
        lab = moves[0]
        for k, a in [(1, "next"), (2, "two"), (3, "three"), (4, "on")]:
            self.at_word(n, a)
            self.play(ptr.animate.move_to(cells[k].get_bottom() + DOWN * 0.4), ReplacementTransform(lab, moves[k]),
                      run_time=0.45)
            lab = moves[k]
        self.play(FadeIn(chain, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.student("zero_05", "So zero doesn't mean the first value is zero. It means its position starts at zero.",
                         "So 0 doesn't mean the first value is 0. Its position starts at 0.")
        self.wait_for_narration(n)

        n = self.teacher("zero_06", "Exactly. That's an important distinction.")
        self.at_word(n, "distinction")
        self.play(ReplacementTransform(chain, point))
        self.play(Indicate(idx[0], color=GOLD, scale_factor=1.4))
        self.wait_for_narration(n)

        self.wipe()
        self.scene_end("S04_zero")

    # ============================================== 5. LET'S TEST IT =====

    def test_it(self):
        self.scene_start("S05_test", title="Let's Test It")

        heading = self.heading("Let's test it", MAIN)
        code = self.card(text("ages = [21, 24, 22, 25, 23]", BODY, MAIN, BOLD), color=MAIN)
        code.next_to(heading, DOWN, buff=0.35).set_x(STAGE_X)
        cells, label = self.named_row("ages", AGES, -0.1)
        idx = index_labels(cells)
        qs = [self.note(s, -1.3, c) for s, c in [("What is stored at index 3?", MAIN), ("ages[3] = 25 ✓", GOLD),
                                                 ("And index 0?", MAIN), ("ages[0] = 21 ✓", GOLD),
                                                 ("What is stored at index 5?", MAIN), ("Count the elements", MAIN),
                                                 ("Valid indexes?", MAIN), ("Does index 5 exist?", MAIN)]]
        count = self.note("5 elements · valid: 0 to 4", -2.0)
        ghost = DashedVMobject(Square(CELL, stroke_color=MUTED, stroke_width=3), num_dashes=16)
        ghost.move_to(cells[-1][0].front.get_center() + RIGHT * CELL)
        ghost_i = text("5 ✗", LABEL, GOLD, BOLD).next_to(ghost, UP, buff=0.22)
        last = self.note("last index = 5 − 1 = 4", -2.7, GOLD)
        self.validator.check_in_frame(VGroup(heading, code, cells, label, idx, ghost, ghost_i, count, last, *qs))

        self.play(FadeIn(heading, shift=DOWN * 0.3), FadeIn(code, shift=UP * 0.15))
        self.play(FadeIn(label), TransformFromCopy(code, cells), FadeIn(idx))

        n = self.teacher("test_01", "Alright, let's test it. What is stored at index three?")
        self.at_word(n, "stored")
        self.play(FadeIn(qs[0], shift=UP * 0.1), self.mark_cell(cells[3]))
        self.wait_for_narration(n)

        n = self.student("test_02", "Twenty-five.", "25.")
        self.wait_for_narration(n)

        n = self.teacher("test_03", "Correct. And index zero?")
        self.at_word(n, "Correct")
        self.play(ReplacementTransform(qs[0], qs[1]))
        self.at_word(n, "zero")
        self.play(ReplacementTransform(qs[1], qs[2]), self.mark_cell(cells[0]))
        self.wait_for_narration(n)

        n = self.student("test_04", "Twenty-one.", "21.")
        self.wait_for_narration(n)

        n = self.teacher("test_05", "Good. Now let's make it slightly tricky. What is stored at index five?")
        self.at_word(n, "Good")
        self.play(ReplacementTransform(qs[2], qs[3]))
        self.at_word(n, "stored")
        self.play(ReplacementTransform(qs[3], qs[4]))
        self.wait_for_narration(n)

        n = self.student("test_06", "Twenty-three.", "23.")
        self.wait_for_narration(n)

        n = self.teacher("test_07", "Let's count the elements first.")
        self.at_word(n, "count")
        self.play(ReplacementTransform(qs[4], qs[5]), LaggedStart(*[Indicate(c, color=GOLD) for c in cells],
                                                                   lag_ratio=0.15))
        self.wait_for_narration(n)

        n = self.student("test_08", "Five elements.")
        self.wait_for_narration(n)

        n = self.teacher("test_09", "And what are the valid indexes?")
        self.at_word(n, "valid")
        self.play(ReplacementTransform(qs[5], qs[6]),
                  LaggedStart(*[Indicate(i_, color=GOLD, scale_factor=1.4) for i_ in idx], lag_ratio=0.15))
        self.wait_for_narration(n)

        n = self.student("test_10", "Zero, one, two, three, four.", "0, 1, 2, 3, 4.")
        self.play(FadeIn(count, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.teacher("test_11", "So does index five exist?")
        self.at_word(n, "exist")
        self.play(ReplacementTransform(qs[6], qs[7]), Create(ghost), FadeIn(ghost_i))
        self.wait_for_narration(n)

        n = self.student("test_12", "No.")
        self.wait_for_narration(n)

        n = self.teacher("test_13", "Exactly. The last index is one less than the number of elements.")
        self.at_word(n, "last")
        self.play(FadeIn(last, shift=UP * 0.1))
        self.add_row(P_LAST, last)
        self.wait_for_narration(n)

        self.wipe()
        self.scene_end("S05_test")

    # =========================================== 6. WHY ARRAYS MATTER ====

    def why_arrays(self):
        self.scene_start("S06_why", title="Why Arrays Matter")

        heading = self.heading("Back to the college system", MAIN)
        x0 = STAGE_LEFT + 0.1
        scale = VGroup(*[pill(s, MUTED, LABEL) for s in ("5 students", "500 students", "5,000 students")])
        scale.arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(heading, DOWN, buff=0.45)
        scale.set_x(x0 + scale.width / 2)
        kinds = VGroup(*[pill(s, MAIN, SMALL) for s in ("marks", "attendance", "scores", "ages", "IDs")])
        kinds.arrange(RIGHT, buff=0.2)
        fit_width(kinds, STAGE_W - 0.4).move_to(RIGHT * STAGE_X + DOWN * 0.7)
        keep = self.note("an array keeps related data together", -1.5, GOLD)
        self.validator.check_in_frame(VGroup(heading, scale, kinds, keep))

        self.play(FadeIn(heading, shift=DOWN * 0.3))
        self.play(LaggedStart(*[FadeIn(p_, shift=DOWN * 0.1) for p_ in scale], lag_ratio=0.3), run_time=1.5)
        n = self.teacher("why_01", "Now think about the college system we started with. Marks, attendance, scores, ages, "
                                   "IDs: there can be thousands of related values.")
        self.at_word(n, "Marks")
        self.play(LaggedStart(*[FadeIn(p_, shift=UP * 0.1) for p_ in kinds], lag_ratio=0.2), run_time=1.5)
        self.wait_for_narration(n)

        n = self.student("why_02", "Creating a separate variable for every value would be difficult.")
        self.wait_for_narration(n)

        n = self.teacher("why_03", "Right. An array gives us a structured way to keep related data together and work with "
                                   "it systematically.")
        self.at_word(n, "structured")
        self.play(FadeIn(keep, shift=UP * 0.1), self.light(P_NAME))
        self.wait_for_narration(n)
        self.wipe()

        heading2 = self.heading("Arrays + loops", GOLD)
        cells, label = self.named_row("marks", MARKS, 1.0)
        loop = self.note("loop: for each element, process it", -0.3)
        frame = SurroundingRectangle(cells[0], color=GOLD, buff=0.06, stroke_width=5)
        chain = VGroup()
        for k, s in enumerate(["One name", "Many values", "Index", "Process all", "Algorithms"]):
            if k:
                chain.add(text("→", LABEL, MUTED, BOLD))
            chain.add(pill(s, GOLD if k == 4 else MAIN, SMALL))
        chain.arrange(RIGHT, buff=0.15)
        fit_width(chain, STAGE_W - 0.4).move_to(RIGHT * STAGE_X + DOWN * 1.9)
        uses = self.note("searching · sorting · algorithms", -2.8, GOLD)
        self.validator.check_in_frame(VGroup(heading2, cells, label, loop, chain, uses))

        self.play(FadeIn(heading2, shift=DOWN * 0.3), FadeIn(label), FadeIn(cells))
        n = self.student("why_04", "And once we combine arrays with loops?")
        self.wait_for_narration(n)

        n = self.teacher("why_05", "Now we're getting somewhere. We can process every element without writing the same "
                                   "instruction again and again. And this idea becomes the foundation for things like "
                                   "searching, sorting, and many algorithms you will use later.")
        self.at_word(n, "process")
        self.play(FadeIn(loop, shift=UP * 0.1), Create(frame))
        for k in range(1, 5):
            self.play(frame.animate.move_to(cells[k]), run_time=0.35)
        self.at_word(n, "foundation")
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in chain], lag_ratio=0.15), run_time=1.5)
        self.at_word(n, "searching")
        self.play(FadeIn(uses, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.wipe()
        self.scene_end("S06_why")

    # ========================================== 7. IN OUR OWN WORDS ======

    def own_words(self):
        self.scene_start("S07_own_words", title="In Our Own Words")

        heading = self.heading("Explain the whole idea yourself", MAIN)
        x, w = self.stage()
        ticks = VGroup(*[tick_row(s, w - 1.6, MAIN, "✓", LABEL, max_lines=2) for s in [
            "One name can hold multiple related values",
            "Each value is an element; we access it with an index",
            "Where does indexing start? At 0",
            "Why arrays? To organise and process collections of data"]])
        ticks.arrange(DOWN, buff=0.3, aligned_edge=LEFT).next_to(heading, DOWN, buff=0.45).set_x(x)
        final = VGroup(text("ARRAY", BODY, GOLD, BOLD))
        for k, s in enumerate(["One name", "Multiple values", "Each value has an index", "Easy access and processing"]):
            final.add(text("↓", LABEL, MUTED, BOLD), pill(s, GOLD if k == 3 else MAIN, LABEL))
        final.arrange(DOWN, buff=0.12).next_to(heading, DOWN, buff=0.35).set_x(x)
        self.validator.check_in_frame(VGroup(heading, ticks))
        self.validator.check_in_frame(VGroup(heading, final))

        n = self.teacher("own_01", "Before we finish, let's see if we can explain the whole idea ourselves.")
        self.at_word(n, "explain")
        self.play(FadeIn(heading, shift=DOWN * 0.3))
        self.wait_for_narration(n)

        n = self.student("own_02", "One name can hold multiple related values.")
        self.play(FadeIn(ticks[0], shift=RIGHT * 0.2), self.light(P_NAME))
        self.wait_for_narration(n)

        n = self.student("own_03", "Each value is an element, and we access it using an index.", who="Another student")
        self.play(FadeIn(ticks[1], shift=RIGHT * 0.2), self.light(P_ELEM, P_INDEX))
        self.wait_for_narration(n)

        n = self.teacher("own_04", "And where does indexing usually start?")
        self.wait_for_narration(n)

        n = self.student("own_05", "Zero!", "Zero!", who="Students")
        self.play(FadeIn(ticks[2], shift=RIGHT * 0.2), self.light(P_INDEX))
        self.wait_for_narration(n)

        n = self.teacher("own_06", "And why are arrays useful?")
        self.wait_for_narration(n)

        n = self.student("own_07", "To organize and process collections of data more easily.")
        self.play(FadeIn(ticks[3], shift=RIGHT * 0.2), self.light(P_NAME, P_ELEM))
        self.wait_for_narration(n)

        n = self.teacher("own_08", "Exactly.")
        self.play(FadeOut(ticks), self.all_lit())
        self.play(LaggedStart(*[FadeIn(m, shift=DOWN * 0.1) for m in final], lag_ratio=0.12), run_time=1.5)
        self.wait_for_narration(n)

        self.final_card = final
        self.scene_end("S07_own_words")

    # ========================================== 8. NEXT SESSION ==========

    def next_session(self):
        self.scene_start("S08_next", title="Next: Array to Memory")

        q = self.question_box("We know how an array looks to us. But where are all these values actually stored inside "
                              "the computer?")
        q.move_to(RIGHT * STAGE_X + UP * 0.9)
        nxt = pill("NEXT SESSION: ARRAY → MEMORY", GOLD, BODY)
        fit_width(nxt, STAGE_W - 0.4).move_to(RIGHT * STAGE_X + DOWN * 0.7)
        self.validator.check_in_frame(VGroup(q, nxt))

        n = self.teacher("next_01", "But there's one question we haven't answered yet.")
        self.at_word(n, "question")
        self.play(FadeOut(self.final_card))
        self.wait_for_narration(n)

        n = self.teacher("next_02", "We know how an array looks to us. But where are all these values actually stored "
                                    "inside the computer?")
        self.at_word(n, "where")
        self.play(FadeIn(q, shift=UP * 0.15))
        self.wait_for_narration(n)

        n = self.student("next_03", "In memory?", who="A student, smiling")
        self.wait_for_narration(n)

        n = self.teacher("next_04", "Exactly. And that's where we'll go next.")
        self.at_word(n, "next")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.undock()
        self.wipe()
        self.scene_end("S08_next")
